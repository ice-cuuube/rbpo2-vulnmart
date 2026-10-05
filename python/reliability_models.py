"""
Модуль математических моделей надёжности программного обеспечения.

Реализованы:
1. Модель Джелински-Моранды.
2. Модель Шумана.
3. Модель Нельсона-Коркорэна.
"""

import math
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np


class JelinskiMorandaModel:
    """Модель Джелински-Моранды."""

    def __init__(self, N0: int, phi: float):
        self.N0 = N0
        self.phi = phi

    def failure_intensity(self, i: int) -> float:
        """Интенсивность отказов после исправления i ошибок."""
        remaining = self.N0 - i

        if remaining < 0:
            raise ValueError(
                "Количество исправленных ошибок "
                "не может превышать начальное"
            )

        return self.phi * remaining

    def reliability(self, t: float, i: int = 0) -> float:
        """Вероятность безотказной работы за время t."""
        lam = self.failure_intensity(i)
        return math.exp(-lam * t)

    def mttf(self, i: int = 0) -> float:
        """Средняя наработка до отказа."""
        lam = self.failure_intensity(i)

        if lam == 0:
            return float("inf")

        return 1.0 / lam


class SchumanModel:
    """Модель Шумана."""

    def __init__(self, I: int, E0: int, Ks: float):
        self.I = I
        self.E0 = E0
        self.Ks = Ks

    def residual_error_density(self, Ec: int) -> float:
        """Удельное число остаточных ошибок."""
        return (self.E0 - Ec) / self.I

    def failure_intensity(self, Ec: int) -> float:
        """Интенсивность отказов."""
        return self.Ks * self.residual_error_density(Ec)

    def reliability(self, t: float, Ec: int = 0) -> float:
        """Вероятность безотказной работы."""
        lam = self.failure_intensity(Ec)
        return math.exp(-lam * t)

    def mttf(self, Ec: int = 0) -> float:
        """Средняя наработка до отказа."""
        lam = self.failure_intensity(Ec)

        if lam == 0:
            return float("inf")

        return 1.0 / lam

    @classmethod
    def estimate_parameters(
        cls,
        I: int,
        t1: float,
        t2: float,
        n1: int,
        n2: int,
        Ec1: int,
        Ec2: int,
    ) -> Tuple[float, float]:
        """
        Оценка параметров E0 и Ks методом моментов.
        """
        if n1 <= 0:
            raise ValueError("n1 должно быть больше 0")

        gamma = (t1 * n2) / (t2 * n1)

        if gamma == 1:
            raise ValueError(
                "Невозможно вычислить E0 при gamma = 1"
            )

        E0 = I * (gamma * Ec1 - Ec2) / (gamma - 1)

        density = (E0 - Ec1) / I

        if density == 0:
            raise ValueError(
                "Невозможно вычислить Ks при нулевой плотности"
            )

        Ks = n1 / (t1 * density)

        return E0, Ks


class NelsonCorcoranModel:
    """Объединённая модель Нельсона-Коркорэна."""

    def __init__(
        self,
        P: List[float],
        n: List[int],
        N: List[int],
        N0: int = None,
        Ni: List[int] = None,
        ai: List[float] = None,
    ):
        if abs(sum(P) - 1.0) > 1e-6:
            raise ValueError(
                "Сумма вероятностей P должна быть равна 1"
            )

        if len(P) != len(n) or len(P) != len(N):
            raise ValueError(
                "Длины списков P, n и N должны совпадать"
            )

        self.P = P
        self.n = n
        self.N = N

        self.N0 = (
            N0 if N0 is not None
            else sum(N) - sum(n)
        )

        self.Ni = Ni

        if ai is not None:
            self.ai = ai
        elif Ni is not None:
            self.ai = [0.5] * len(Ni)
        else:
            self.ai = []

    def reliability_nelson(self) -> float:
        """Надёжность по подходу Нельсона."""
        failure_prob = sum(
            (ni / Ni) * Pi
            for ni, Ni, Pi
            in zip(self.n, self.N, self.P)
        )

        return 1.0 - failure_prob

    def reliability_corcoran(self) -> float:
        """Надёжность по расширению Коркорэна."""
        if not self.Ni:
            return self.reliability_simple()

        if len(self.Ni) != len(self.ai):
            raise ValueError(
                "Размеры Ni и ai должны совпадать"
            )

        sum_term = sum(
            self.ai[i] * (self.Ni[i] - 1)
            for i in range(len(self.Ni))
            if self.Ni[i] > 0
        )

        N_total = self.N0 + sum(self.Ni)

        return (self.N0 + sum_term) / N_total

    def reliability_simple(self) -> float:
        """Упрощённая форма."""
        n_failures = sum(self.n)
        n_total = sum(self.N)

        return 1.0 - n_failures / n_total

    def reliability(self) -> float:
        """Основная оценка надёжности по Нельсону."""
        return self.reliability_nelson()


def demo_calculations():
    """Выполняет демонстрационные расчёты."""
    print("=" * 70)
    print("РАСЧЁТ НАДЁЖНОСТИ ПО МОДЕЛЯМ")
    print("=" * 70)

    print("\n1. МОДЕЛЬ ДЖЕЛИНСКИ-МОРАНДЫ")

    jm = JelinskiMorandaModel(
        N0=50,
        phi=0.0001
    )

    print(
        " Интенсивность отказов (i=30): "
        f"{jm.failure_intensity(30):.6f} отказов/час"
    )

    print(
        f" R(t=100) = {jm.reliability(100, i=30):.4f}"
    )

    print(
        f" MTTF = {jm.mttf(i=30):.2f} часов"
    )

    print("\n2. МОДЕЛЬ ШУМАНА")

    sch = SchumanModel(
        I=10000,
        E0=50,
        Ks=0.0001
    )

    print(
        " Удельное число остаточных ошибок: "
        f"{sch.residual_error_density(30):.6f}"
    )

    print(
        " Интенсивность отказов: "
        f"{sch.failure_intensity(30):.8f}"
    )

    print(
        f" R(t=100) = {sch.reliability(100, Ec=30):.8f}"
    )

    print(
        f" MTTF = {sch.mttf(Ec=30):.0f} часов"
    )

    print("\n3. МОДЕЛЬ НЕЛЬСОНА-КОРКОРЭНА")

    nc = NelsonCorcoranModel(
        P=[0.6, 0.4],
        n=[5, 2],
        N=[100, 50],
        N0=970,
        Ni=[20, 10],
        ai=[0.7, 0.3],
    )

    print(
        " R (Нельсон, через подобласти) = "
        f"{nc.reliability_nelson():.4f}"
    )

    print(
        " R (Коркорэн, с типами ошибок) = "
        f"{nc.reliability_corcoran():.4f}"
    )

    print(
        f" R (упрощённая) = "
        f"{nc.reliability_simple():.4f}"
    )


def plot_reliability_curves():
    """Строит графики надёжности от времени."""

    t = np.linspace(1, 500, 100)

    jm = JelinskiMorandaModel(
        N0=50,
        phi=0.0001
    )

    sch = SchumanModel(
        I=10000,
        E0=50,
        Ks=0.0001
    )

    R_jm = [
        jm.reliability(time, i=30)
        for time in t
    ]

    R_sch = [
        sch.reliability(time, Ec=30)
        for time in t
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        t,
        R_jm,
        label="Джелински-Моранды",
        linewidth=2
    )

    plt.plot(
        t,
        R_sch,
        label="Шумана",
        linewidth=2
    )

    plt.axhline(
        y=0.95,
        linestyle=":",
        label="Целевой уровень R=0.95"
    )

    plt.xlabel("Время наработки, часы")
    plt.ylabel("Вероятность безотказной работы R(t)")
    plt.title("Сравнение моделей надёжности ПО")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        "reliability_curves.png",
        dpi=150
    )

    print(
        "\nГрафик сохранён: "
        "reliability_curves.png"
    )


demo_calculations()
plot_reliability_curves()
