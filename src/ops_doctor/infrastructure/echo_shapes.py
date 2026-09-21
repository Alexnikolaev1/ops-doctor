"""Shape analysis via Echo Matrix Profile (library import)."""

from __future__ import annotations

from echo.use_cases.analyze_time_series import AnalyzeRequest, AnalyzeTimeSeriesUseCase

from ops_doctor.entities.host import ShapeFinding


class EchoShapeAnalyzer:
    def __init__(self) -> None:
        self._analyze = AnalyzeTimeSeriesUseCase()

    def find_weird(
        self, metric: str, values: tuple[float, ...], window: int, min_distance: float
    ) -> ShapeFinding:
        if len(values) < window * 2:
            return ShapeFinding(metric, False, 0.0, -1, "not enough points")
        try:
            report = self._analyze.execute(
                AnalyzeRequest(values=values, subsequence_length=window, top_k=1)
            )
        except ValueError as exc:
            return ShapeFinding(metric, False, 0.0, -1, f"skipped: {exc}")
        if not report.discords:
            return ShapeFinding(metric, False, 0.0, -1, "no discords")
        discord = report.discords[0]
        weird = discord.distance_to_nearest_neighbor >= min_distance
        return ShapeFinding(
            metric=metric,
            weird=weird,
            distance=discord.distance_to_nearest_neighbor,
            start_index=discord.start_index,
            explanation=discord.explanation(),
        )
