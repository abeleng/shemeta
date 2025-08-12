# pip install pandas numpy
import numpy as np
import pandas as pd
from dataclasses import dataclass

# -----------------------------
# Penalty helpers
# -----------------------------
def range_penalty(x, xmin, xopt, xmax, w_in=1.0, w_under=2.0, w_over=1.8):
    """
    Asymmetric penalty for scalar x against crop's acceptable [xmin, xopt, xmax].
    - Inside [xmin,xmax]: small penalty by distance from xopt (normalized by span)
    - Below min / above max: sharper penalties
    """
    span = max(1e-6, xmax - xmin)
    if x < xmin:  return w_under * (xmin - x) / span
    if x > xmax:  return w_over  * (x - xmax) / span
    return w_in * abs(x - xopt) / span

def window_distance(doy, start, end, wrap=365):
    """
    Distance (days) from DOY to inclusive window [start,end] on a circular year.
    0 if inside; otherwise min days to reach boundary.
    """
    doy, start, end = int(doy), int(start), int(end)
    if start <= end:
        if start <= doy <= end: return 0
        # how far to get into window (forward/back)
        return min((start - doy) % wrap, (doy - end) % wrap)
    else:
        # window wraps year end
        if doy >= start or doy <= end: return 0
        return min((start - doy) % wrap, (doy - end) % wrap)

def clamp_pos(x): return max(0.0, float(x))

# -----------------------------
# Feature groups (CSV side)
# -----------------------------
NDVI_CROP_FEATURES = [
    "ndvi_peak","ndvi_scale","ndvi_seasonal_avg",
    "ndvi_start_of_season","ndvi_end_of_season",
    "ndvi_integral","ndvi_threshold","ndvi_anomaly_avg"
]

RAINFALL_CROP_FEATURES = [
    "seasonal_rainfall_total_min","seasonal_rainfall_total_opt","seasonal_rainfall_total_max",
    "onset_date","cessation_date",
    "rainy_days_count","dry_spell_days",
    "onset_delay_days","onset_threshold","rainy_day_threshold","dry_spell_threshold",
    "rainfall_std_dev","rainfall_skewness","data_quality_flag"
]

SOIL_MOIST_CROP_FEATURES = [
    "mean_soil_moisture","dry_soil_days","dry_threshold","soil_moisture_std"
]

TEMP_CROP_FEATURES = [
    "mean_temp_season_min","mean_temp_season_max","max_temp_avg","min_temp_avg",
    "gdd_total","gdd_base_temp","heatwave_days","heatwave_threshold"
]

# -----------------------------
# Weights (tune as needed)
# -----------------------------
@dataclass
class Weights:
    # group-level
    ndvi: float = 0.8
    rainfall: float = 1.2
    soil_moisture: float = 1.0
    temperature_mean: float = 1.0
    temperature_extremes: float = 1.2
    gdd: float = 0.8
    heatwaves: float = 1.0
    sow_window: float = 0.6
    onset_dynamics: float = 0.6
    rainy_days_min: float = 0.9
    dry_spells: float = 1.0
    variability: float = 0.5
    # area data quality (optional nudge 0..1)
    area_quality_alpha: float = 0.0

class CropEnvMatcherForKebele:
    """
    For each crop in crop_df, evaluate compatibility against matching area instances
    (list of dicts with "crop" and environment features). Returns per-crop min distance.
    """

    def __init__(self, weights: Weights | None = None):
        self.w = weights or Weights()
        self.crop_df = None

    # ---------- Fit ----------
    def fit(self, crop_df: pd.DataFrame):
        required_cols = ["crop"] + NDVI_CROP_FEATURES + RAINFALL_CROP_FEATURES + SOIL_MOIST_CROP_FEATURES + TEMP_CROP_FEATURES
        miss = [c for c in required_cols if c not in crop_df.columns]
        if miss:
            raise ValueError(f"Crop CSV missing columns: {miss}")
        self.crop_df = crop_df.reset_index(drop=True).copy()
        return self

    # ---------- Distance ----------
    def _distance_one(self, crop: pd.Series, area: dict) -> float:
        w = self.w

        # ---- NDVI: compare like-for-like (absolute/normalized diffs)
        # You can tighten/loosen normalization divisors per dataset.
        p_ndvi = (
            abs(area["ndvi_peak"] - crop["ndvi_peak"]) / max(0.1, crop["ndvi_peak"]) +
            0.3 * abs(area["ndvi_scale"] - crop["ndvi_scale"]) / max(0.1, crop["ndvi_scale"]) +
            abs(area["ndvi_seasonal_avg"] - crop["ndvi_seasonal_avg"]) / max(0.1, crop["ndvi_seasonal_avg"]) +
            0.01 * abs(area["ndvi_start_of_season"] - crop["ndvi_start_of_season"]) +  # DOY diff (~days)
            0.01 * abs(area["ndvi_end_of_season"] - crop["ndvi_end_of_season"]) +
            clamp_pos(crop["ndvi_integral"] - area["ndvi_integral"]) / max(1.0, crop["ndvi_integral"]) +  # penalize if area integral < required
            0.5 * clamp_pos(crop["ndvi_threshold"] - area["ndvi_threshold"]) / max(0.05, crop["ndvi_threshold"]) +
            0.5 * clamp_pos(abs(area["ndvi_anomaly_avg"]) - abs(crop["ndvi_anomaly_avg"])) / max(0.05, abs(crop["ndvi_anomaly_avg"]))
        ) * w.ndvi

        # ---- Rainfall total: range penalty with (min,opt,max) from crop; area must provide 'seasonal_rainfall_total'
        p_rain_total = range_penalty(
            x=area["seasonal_rainfall_total"],
            xmin=crop["seasonal_rainfall_total_min"],
            xopt=crop["seasonal_rainfall_total_opt"],
            xmax=crop["seasonal_rainfall_total_max"],
            w_in=1.0, w_under=2.2, w_over=1.6
        )

        # ---- Sowing window vs area onset date
        sow_days = window_distance(area["onset_date"], crop["onset_date"], crop["cessation_date"])
        window_len = ((crop["cessation_date"] - crop["onset_date"]) % 365) or 30
        p_sow = (sow_days / max(1.0, window_len)) * w.sow_window

        # ---- Rainy days minimum
        p_rainy_min = clamp_pos(crop["rainy_days_count"] - area["rainy_days_count"]) / max(1.0, crop["rainy_days_count"]) * w.rainy_days_min

        # ---- Dry spells tolerance (consecutive days + definition)
        p_dry_consec = clamp_pos(area["dry_spell_days"] - crop["dry_spell_days"]) / max(1.0, crop["dry_spell_days"])
        p_dry_def = 0.2 * abs(area["dry_spell_threshold"] - crop["dry_spell_threshold"]) / max(1.0, crop["dry_spell_threshold"])
        p_dry = (p_dry_consec + p_dry_def) * w.dry_spells

        # ---- Onset dynamics and thresholds
        p_onset_delay = clamp_pos(area["onset_delay_days"] - crop["onset_delay_days"]) / max(1.0, crop["onset_delay_days"])
        p_onset_mm = 0.4 * abs(area["onset_threshold"] - crop["onset_threshold"]) / max(5.0, crop["onset_threshold"])
        p_rainydef = 0.3 * abs(area["rainy_day_threshold"] - crop["rainy_day_threshold"]) / max(1.0, crop["rainy_day_threshold"])
        p_onset = (p_onset_delay + p_onset_mm + p_rainydef) * w.onset_dynamics

        # ---- Rainfall variability tolerances
        var_excess = clamp_pos(area["rainfall_std_dev"] - crop["rainfall_std_dev"]) / max(1.0, crop["rainfall_std_dev"])
        skew_mismatch = abs(area["rainfall_skewness"] - crop["rainfall_skewness"]) / max(0.2, abs(crop["rainfall_skewness"]))
        p_var = (var_excess + 0.3 * skew_mismatch) * w.variability

        p_rain = (p_rain_total + p_sow + p_rainy_min + p_dry + p_onset + p_var) * w.rainfall

        # ---- Soil moisture requirements/tolerances
        p_sm_min = clamp_pos(crop["mean_soil_moisture"] - area["mean_soil_moisture"]) / max(1.0, crop["mean_soil_moisture"])
        p_sm_drydays = clamp_pos(area["dry_soil_days"] - crop["dry_soil_days"]) / max(1.0, crop["dry_soil_days"])
        p_sm_thresh = clamp_pos(crop["dry_threshold"] - area["dry_threshold"]) / max(1.0, crop["dry_threshold"])
        p_sm_var = abs(area["soil_moisture_std"] - crop["soil_moisture_std"]) / max(1.0, crop["soil_moisture_std"])
        p_soil = (p_sm_min + 0.7*p_sm_drydays + 0.5*p_sm_thresh + 0.3*p_sm_var) * w.soil_moisture

        # ---- Temperature (mean range)
        # area must supply 'mean_temp_season'
        opt_center = 0.5*(crop["mean_temp_season_min"] + crop["mean_temp_season_max"])
        p_t_mean = range_penalty(
            x=area["mean_temp_season"],
            xmin=crop["mean_temp_season_min"],
            xopt=opt_center,
            xmax=crop["mean_temp_season_max"],
            w_in=1.0, w_under=2.0, w_over=2.0
        ) * w.temperature_mean

        # ---- Temperature extremes
        p_t_max = clamp_pos(area["max_temp_avg"] - crop["max_temp_avg"]) / max(1.0, crop["max_temp_avg"])
        p_t_min = clamp_pos(crop["min_temp_avg"] - area["min_temp_avg"]) / max(1.0, abs(crop["min_temp_avg"]))
        p_text = (p_t_max + p_t_min) * w.temperature_extremes

        # ---- GDD & base temp
        p_gdd = abs(area["gdd_total"] - crop["gdd_total"]) / max(50.0, crop["gdd_total"])
        p_gdd += 0.2 * abs(area["gdd_base_temp"] - crop["gdd_base_temp"]) / max(1.0, crop["gdd_base_temp"])
        p_gdd *= w.gdd

        # ---- Heatwaves
        p_hw_days = clamp_pos(area["heatwave_days"] - crop["heatwave_days"]) / max(1.0, crop["heatwave_days"])
        p_hw_thr  = 0.2 * abs(area["heatwave_threshold"] - crop["heatwave_threshold"]) / max(1.0, crop["heatwave_threshold"])
        p_heat = (p_hw_days + p_hw_thr) * w.heatwaves

        dist = p_ndvi + p_rain + p_soil + p_t_mean + p_text + p_gdd + p_heat

        # Optional nudge for area data quality (0..1) to slightly reward high-quality inputs
        if "data_quality_flag" in area and w.area_quality_alpha > 0:
            q = float(area["data_quality_flag"])
            dist = dist / (1.0 + w.area_quality_alpha * np.clip(q, 0.0, 1.0))

        return float(dist)

    # ---------- Query ----------
    def query_kebele(self, area_instances: list[dict], max_distance: float = 25.0, return_all=True) -> pd.DataFrame:
        """
        area_instances: list of dicts; EACH dict must include:
            "crop" plus all area-side keys referenced in _distance_one:
            ndvi_* , seasonal_rainfall_total, onset_date, cessation_date, rainy_days_count,
            dry_spell_days, onset_delay_days, onset_threshold, rainy_day_threshold, dry_spell_threshold,
            rainfall_std_dev, rainfall_skewness, data_quality_flag,
            mean_soil_moisture, dry_soil_days, dry_threshold, soil_moisture_std,
            mean_temp_season, max_temp_avg, min_temp_avg, gdd_total, gdd_base_temp, heatwave_days, heatwave_threshold
        For each crop in crop_df, we find matching area dicts (by "crop") and take the MIN distance.
        """
        assert self.crop_df is not None, "Call fit(crop_df) first."

        # Print crop names for debugging
        print("Crop names in crop_df:", list(self.crop_df["crop"]))
        print("Crop names in area_instances:", [d.get("crop") for d in area_instances])

        # Index area instances by Crop for quick lookup
        by_crop = {}
        for d in area_instances:
            c = d.get("crop")
            if c is None: continue
            by_crop.setdefault(c, []).append(d)

        rows = []
        for i, crop in self.crop_df.iterrows():
            crop_name = crop["crop"]
            if crop_name not in by_crop:
                continue  # no area instance for this crop in this kebele
            # compute distance for all instances of this crop; keep min
            dists = [self._distance_one(crop, a) for a in by_crop[crop_name]]
            best_idx = int(np.argmin(dists))
            best_dist = float(dists[best_idx])
            best_area = by_crop[crop_name][best_idx]
            print(f"Crop: {crop_name}, Best Distance: {best_dist}")
            # Only append if best_dist <= max_distance
            if best_dist <= max_distance:
                rows.append({
                    "crop": crop_name,
                    "distance": best_dist,
                    "best_area_index": best_idx,
                    "seasonal_rainfall_total": best_area.get("seasonal_rainfall_total"),
                    "mean_temp_season": best_area.get("mean_temp_season"),
                    "data_quality_flag": best_area.get("data_quality_flag"),
                    "ndvi_peak": best_area.get("ndvi_peak"),  # <-- Add this line
                })

        out = pd.DataFrame(rows)
        if not out.empty and "distance" in out.columns:
            out = out.sort_values("distance").reset_index(drop=True)
        print("Matches found:", out.to_dict(orient="records"))
        return out

# -----------------------------
# Minimal example
# -----------------------------
# if __name__ == "__main__":
#     # Example crop CSV (columns truncated for brevity; include all in real data)
#     crop_df = pd.DataFrame({
#         "crop": ["Maize","Wheat","Green Bean"],
#         # NDVI (illustrative)
#         "ndvi_peak":[0.62,0.58,0.55], "ndvi_scale":[1.0,1.0,1.0], "ndvi_seasonal_avg":[0.42,0.40,0.39],
#         "ndvi_start_of_season":[120,110,112], "ndvi_end_of_season":[270,250,240],
#         "ndvi_integral":[35,32,25], "ndvi_threshold":[0.2,0.2,0.18], "ndvi_anomaly_avg":[0.05,0.04,0.05],
#         # Rainfall ranges & tolerances
#         "seasonal_rainfall_total_min":[500,420,550], "seasonal_rainfall_total_opt":[650,520,650], "seasonal_rainfall_total_max":[850,700,800],
#         "onset_date":[110,100,102], "cessation_date":[150,140,150],
#         "rainy_days_count":[35,30,36], "dry_spell_days":[10,7,9],
#         "onset_delay_days":[12,10,10], "onset_threshold":[20,15,18], "rainy_day_threshold":[2.5,2.0,2.5], "dry_spell_threshold":[5,4,4],
#         "rainfall_std_dev":[90,70,80], "rainfall_skewness":[0.2,0.1,0.15], "data_quality_flag":[1,1,1],
#         # Soil moisture
#         "mean_soil_moisture":[30,28,29], "dry_soil_days":[6,5,6], "dry_threshold":[15,15,15], "soil_moisture_std":[5,5,5],
#         # Temperature & GDD & heat
#         "mean_temp_season_min":[18,14,18], "mean_temp_season_max":[26,20,24],
#         "max_temp_avg":[30,26,28], "min_temp_avg":[8,2,10],
#         "gdd_total":[1400,1200,1100], "gdd_base_temp":[10,5,10],
#         "heatwave_days":[4,2,3], "heatwave_threshold":[33,30,32],
#     })

#     kebele_area_instances = [
#         # One dict per crop observed/predicted in this kebele
#         {"crop":"Maize",
#          "ndvi_peak":0.60,"ndvi_scale":1.0,"ndvi_seasonal_avg":0.41,"ndvi_start_of_season":118,"ndvi_end_of_season":268,
#          "ndvi_integral":34.5,"ndvi_threshold":0.20,"ndvi_anomaly_avg":0.04,
#          "seasonal_rainfall_total":640,"onset_date":120,"cessation_date":268,
#          "rainy_days_count":40,"dry_spell_days":9,"onset_delay_days":11,"onset_threshold":20,"rainy_day_threshold":2.5,"dry_spell_threshold":5.0,
#          "rainfall_std_dev":88,"rainfall_skewness":0.18,"data_quality_flag":0.95,
#          "mean_soil_moisture":31,"dry_soil_days":5,"dry_threshold":15,"soil_moisture_std":5,
#          "mean_temp_season":21.2,"max_temp_avg":28,"min_temp_avg":10,
#          "gdd_total":1450,"gdd_base_temp":10,"heatwave_days":3,"heatwave_threshold":33},

#         {"crop":"Wheat",
#          "ndvi_peak":0.57,"ndvi_scale":1.0,"ndvi_seasonal_avg":0.40,"ndvi_start_of_season":108,"ndvi_end_of_season":248,
#          "ndvi_integral":31.5,"ndvi_threshold":0.20,"ndvi_anomaly_avg":0.04,
#          "seasonal_rainfall_total":510,"onset_date":104,"cessation_date":246,
#          "rainy_days_count":32,"dry_spell_days":7,"onset_delay_days":9,"onset_threshold":15,"rainy_day_threshold":2.0,"dry_spell_threshold":4.0,
#          "rainfall_std_dev":72,"rainfall_skewness":0.10,"data_quality_flag":0.9,
#          "ndvi_peak":0.57,"ndvi_scale":1.0,"ndvi_seasonal_avg":0.40,"ndvi_start_of_season":108,"ndvi_end_of_season":248,
#          "ndvi_integral":31.5,"ndvi_threshold":0.20,"ndvi_anomaly_avg":0.04,
#          "seasonal_rainfall_total":510,"onset_date":104,"cessation_date":246,
#          "rainy_days_count":32,"dry_spell_days":7,"onset_delay_days":9,"onset_threshold":15,"rainy_day_threshold":2.0,"dry_spell_threshold":4.0,
#          "rainfall_std_dev":72,"rainfall_skewness":0.10,"data_quality_flag":0.9,
#          "mean_soil_moisture":29,"dry_soil_days":5,"dry_threshold":15,"soil_moisture_std":5,
#          "mean_temp_season":18.3,"max_temp_avg":25,"min_temp_avg":6,
#          "gdd_total":1190,"gdd_base_temp":5,"heatwave_days":1,"heatwave_threshold":30},

#         {"crop":"Green Bean",
#          "ndvi_peak":0.55,"ndvi_scale":1.0,"ndvi_seasonal_avg":0.39,"ndvi_start_of_season":110,"ndvi_end_of_season":238,
#          "ndvi_integral":24.0,"ndvi_threshold":0.18,"ndvi_anomaly_avg":0.05,
#          "seasonal_rainfall_total":660,"onset_date":106,"cessation_date":240,
#          "rainy_days_count":36,"dry_spell_days":8,"onset_delay_days":8,"onset_threshold":18,"rainy_day_threshold":2.5,"dry_spell_threshold":4.0,
#          "rainfall_std_dev":82,"rainfall_skewness":0.16,"data_quality_flag":0.85,
#          "mean_soil_moisture":30,"dry_soil_days":6,"dry_threshold":15,"soil_moisture_std":5,
#          "mean_temp_season":22,"max_temp_avg":27,"min_temp_avg":12,
#          "gdd_total":1120,"gdd_base_temp":10,"heatwave_days":2,"heatwave_threshold":32},
#     ]

#     matcher = CropEnvMatcherForKebele().fit(crop_df)
#     results = matcher.query_kebele(kebele_area_instances, max_distance=3.0, return_all=False)
#     print(results)
