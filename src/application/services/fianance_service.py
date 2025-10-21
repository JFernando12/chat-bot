from domain.finance import FinanceCalculator, FinancingPlan

class FinanceService:
    """Encapsula la lógica de cálculo y conversión a dict."""

    @staticmethod
    def calculate_plan(price: float, enganche: float, years: int, annual_rate: float = 0.10) -> dict[str, float]:
        plan = FinanceCalculator.calculate(price, enganche, annual_rate, years)
        return FinanceCalculator.to_dict(plan)

    @staticmethod
    def describe_plan(plan: FinancingPlan) -> str:
        return (
            f"Precio financiado: ${plan.financed_amount:,.0f}\n"
            f"Pago mensual: ${plan.monthly_payment:,.0f} por {plan.months} meses\n"
            f"Total pagado: ${plan.total_paid:,.0f}\n"
            f"Intereses: ${plan.total_interest:,.0f}"
        )
