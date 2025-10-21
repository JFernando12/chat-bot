from dataclasses import dataclass

@dataclass(frozen=True)
class FinancingPlan:
    financed_amount: float
    monthly_payment: float
    total_paid: float
    total_interest: float
    months: int

class FinanceCalculator:
    """Reglas de negocio para cálculo de planes de financiamiento."""

    @staticmethod
    def calculate(price: float, enganche: float, annual_rate: float, years: int) -> FinancingPlan:
        if years < 3 or years > 6:
            raise ValueError("El plazo debe estar entre 3 y 6 años.")
        financed = price - enganche
        if financed <= 0:
            return FinancingPlan(
                financed_amount=0,
                monthly_payment=0,
                total_paid=enganche,
                total_interest=0,
                months=0
            )
        n = years * 12
        r = annual_rate / 12.0
        monthly = (r * financed) / (1.0 - (1.0 + r) ** (-n))
        total_paid = monthly * n + enganche
        total_interest = monthly * n - financed
        return FinancingPlan(
            financed_amount=round(financed, 2),
            monthly_payment=round(monthly, 2),
            total_paid=round(total_paid, 2),
            total_interest=round(total_interest, 2),
            months=n
        )

    @staticmethod
    def to_dict(plan: FinancingPlan) -> dict[str, float]:
        return {
            "financed_amount": plan.financed_amount,
            "monthly_payment": plan.monthly_payment,
            "total_paid": plan.total_paid,
            "total_interest": plan.total_interest,
            "months": plan.months
        }
