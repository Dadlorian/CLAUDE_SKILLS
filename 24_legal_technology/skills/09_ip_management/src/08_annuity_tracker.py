"""
Patent Annuity Tracker
Tracks and calculates patent annuity (renewal) fees across jurisdictions
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal

logger = logging.getLogger(__name__)


class Currency(Enum):
    """Currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    CHF = "CHF"


@dataclass
class AnnuityFee:
    """Annuity fee details"""
    year: int
    amount: Decimal
    currency: Currency
    jurisdiction: str
    due_date: datetime
    paid: bool = False
    payment_date: Optional[datetime] = None
    late_payment_fee: Decimal = Decimal("0.00")


@dataclass
class PatentAnnuities:
    """Patent annuity information"""
    patent_number: str
    jurisdiction: str
    issue_date: datetime
    expiration_date: datetime
    annuities: List[AnnuityFee] = field(default_factory=list)
    total_cost: Decimal = Decimal("0.00")
    maintenance_status: str = "active"


class AnnuityCalculator:
    """Calculate patent annuity fees"""

    def __init__(self):
        """Initialize annuity calculator"""
        self.fee_schedules = self._load_fee_schedules()
        self.exchange_rates = self._load_exchange_rates()

    def calculate_annuities(
        self,
        patent_number: str,
        issue_date: datetime,
        jurisdiction: str = "US"
    ) -> PatentAnnuities:
        """
        Calculate all annuity fees for a patent

        Args:
            patent_number: Patent number
            issue_date: Patent issue date
            jurisdiction: Patent jurisdiction

        Returns:
            PatentAnnuities object
        """
        try:
            if jurisdiction == "US":
                annuities = self._calculate_us_annuities(patent_number, issue_date)
            elif jurisdiction == "EP":
                annuities = self._calculate_ep_annuities(patent_number, issue_date)
            elif jurisdiction == "JP":
                annuities = self._calculate_jp_annuities(patent_number, issue_date)
            elif jurisdiction == "CN":
                annuities = self._calculate_cn_annuities(patent_number, issue_date)
            elif jurisdiction == "GB":
                annuities = self._calculate_gb_annuities(patent_number, issue_date)
            else:
                logger.warning(f"Unknown jurisdiction: {jurisdiction}")
                annuities = PatentAnnuities(
                    patent_number=patent_number,
                    jurisdiction=jurisdiction,
                    issue_date=issue_date,
                    expiration_date=issue_date + timedelta(days=20*365)
                )

            # Calculate total cost
            annuities.total_cost = sum(f.amount for f in annuities.annuities)

            return annuities

        except Exception as e:
            logger.error(f"Failed to calculate annuities: {e}")
            return PatentAnnuities(
                patent_number=patent_number,
                jurisdiction=jurisdiction,
                issue_date=issue_date,
                expiration_date=issue_date + timedelta(days=20*365)
            )

    def _calculate_us_annuities(
        self,
        patent_number: str,
        issue_date: datetime
    ) -> PatentAnnuities:
        """Calculate US patent maintenance fees"""
        # US patents have 3 maintenance fee periods
        # First at 3.5 years, second at 7 years, third at 11.5 years

        annuities = PatentAnnuities(
            patent_number=patent_number,
            jurisdiction="US",
            issue_date=issue_date,
            expiration_date=issue_date + timedelta(days=20*365)
        )

        maintenance_fees = [
            (3.5, Decimal("1600")),   # 3.5 years - large entity
            (7, Decimal("3600")),      # 7 years - large entity
            (11.5, Decimal("5400")),   # 11.5 years - large entity
        ]

        for years, fee in maintenance_fees:
            due_date = issue_date + timedelta(days=years*365)

            annuities.annuities.append(AnnuityFee(
                year=int(years),
                amount=fee,
                currency=Currency.USD,
                jurisdiction="US",
                due_date=due_date
            ))

        return annuities

    def _calculate_ep_annuities(
        self,
        patent_number: str,
        issue_date: datetime
    ) -> PatentAnnuities:
        """Calculate European patent renewal fees"""
        # EP patents have annual renewal fees from year 3 onwards
        annuities = PatentAnnuities(
            patent_number=patent_number,
            jurisdiction="EP",
            issue_date=issue_date,
            expiration_date=issue_date + timedelta(days=20*365)
        )

        # European fee schedule (simplified)
        ep_fees = {
            3: Decimal("600"),
            4: Decimal("700"),
            5: Decimal("800"),
            6: Decimal("900"),
            7: Decimal("1000"),
            8: Decimal("1200"),
            9: Decimal("1400"),
            10: Decimal("1600"),
            11: Decimal("1800"),
            12: Decimal("2000"),
            13: Decimal("2200"),
            14: Decimal("2400"),
            15: Decimal("2600"),
            16: Decimal("2800"),
            17: Decimal("3000"),
            18: Decimal("3200"),
            19: Decimal("3400"),
            20: Decimal("3600"),
        }

        for year, fee in ep_fees.items():
            due_date = issue_date + timedelta(days=year*365)

            annuities.annuities.append(AnnuityFee(
                year=year,
                amount=fee,
                currency=Currency.EUR,
                jurisdiction="EP",
                due_date=due_date
            ))

        return annuities

    def _calculate_jp_annuities(
        self,
        patent_number: str,
        issue_date: datetime
    ) -> PatentAnnuities:
        """Calculate Japanese patent annuity fees"""
        annuities = PatentAnnuities(
            patent_number=patent_number,
            jurisdiction="JP",
            issue_date=issue_date,
            expiration_date=issue_date + timedelta(days=20*365)
        )

        # Japanese fee schedule (JPY)
        jp_fees = {
            1: Decimal("2100"),
            2: Decimal("3400"),
            3: Decimal("4400"),
            4: Decimal("5600"),
            5: Decimal("6900"),
            6: Decimal("8100"),
            7: Decimal("9400"),
            8: Decimal("10700"),
            9: Decimal("12000"),
            10: Decimal("13400"),
            11: Decimal("14700"),
            12: Decimal("16000"),
            13: Decimal("17300"),
            14: Decimal("18700"),
            15: Decimal("20000"),
            16: Decimal("21300"),
            17: Decimal("22700"),
            18: Decimal("24000"),
            19: Decimal("25300"),
            20: Decimal("26700"),
        }

        for year, fee in jp_fees.items():
            due_date = issue_date + timedelta(days=year*365)

            annuities.annuities.append(AnnuityFee(
                year=year,
                amount=fee,
                currency=Currency.JPY,
                jurisdiction="JP",
                due_date=due_date
            ))

        return annuities

    def _calculate_cn_annuities(
        self,
        patent_number: str,
        issue_date: datetime
    ) -> PatentAnnuities:
        """Calculate Chinese patent annuity fees"""
        annuities = PatentAnnuities(
            patent_number=patent_number,
            jurisdiction="CN",
            issue_date=issue_date,
            expiration_date=issue_date + timedelta(days=20*365)
        )

        # Chinese fee schedule (CNY)
        cn_fees = {
            1: Decimal("150"),
            2: Decimal("150"),
            3: Decimal("200"),
            4: Decimal("200"),
            5: Decimal("300"),
            6: Decimal("400"),
            7: Decimal("500"),
            8: Decimal("600"),
            9: Decimal("700"),
            10: Decimal("800"),
            11: Decimal("900"),
            12: Decimal("1000"),
            13: Decimal("1100"),
            14: Decimal("1200"),
            15: Decimal("1300"),
            16: Decimal("1400"),
            17: Decimal("1500"),
            18: Decimal("1600"),
            19: Decimal("1700"),
            20: Decimal("1800"),
        }

        for year, fee in cn_fees.items():
            due_date = issue_date + timedelta(days=year*365)

            annuities.annuities.append(AnnuityFee(
                year=year,
                amount=fee,
                currency=Currency.CNY,
                jurisdiction="CN",
                due_date=due_date
            ))

        return annuities

    def _calculate_gb_annuities(
        self,
        patent_number: str,
        issue_date: datetime
    ) -> PatentAnnuities:
        """Calculate UK patent renewal fees"""
        annuities = PatentAnnuities(
            patent_number=patent_number,
            jurisdiction="GB",
            issue_date=issue_date,
            expiration_date=issue_date + timedelta(days=20*365)
        )

        # UK fee schedule (GBP)
        gb_fees = {
            5: Decimal("50"),
            6: Decimal("70"),
            7: Decimal("100"),
            8: Decimal("130"),
            9: Decimal("160"),
            10: Decimal("190"),
            11: Decimal("220"),
            12: Decimal("250"),
            13: Decimal("280"),
            14: Decimal("310"),
            15: Decimal("340"),
            16: Decimal("370"),
            17: Decimal("400"),
            18: Decimal("430"),
            19: Decimal("460"),
            20: Decimal("490"),
        }

        for year, fee in gb_fees.items():
            due_date = issue_date + timedelta(days=year*365)

            annuities.annuities.append(AnnuityFee(
                year=year,
                amount=fee,
                currency=Currency.GBP,
                jurisdiction="GB",
                due_date=due_date
            ))

        return annuities

    def _load_fee_schedules(self) -> Dict[str, List]:
        """Load annuity fee schedules"""
        return {}

    def _load_exchange_rates(self) -> Dict[Tuple[Currency, Currency], Decimal]:
        """Load currency exchange rates"""
        return {}


class AnnuityTracker:
    """Track annuity payment status"""

    def __init__(self, calculator: AnnuityCalculator):
        """
        Initialize tracker

        Args:
            calculator: AnnuityCalculator instance
        """
        self.calculator = calculator
        self.patents = {}

    def add_patent(
        self,
        patent_number: str,
        issue_date: datetime,
        jurisdiction: str = "US"
    ) -> None:
        """
        Add patent to tracker

        Args:
            patent_number: Patent number
            issue_date: Patent issue date
            jurisdiction: Patent jurisdiction
        """
        annuities = self.calculator.calculate_annuities(
            patent_number,
            issue_date,
            jurisdiction
        )
        self.patents[patent_number] = annuities

    def record_payment(
        self,
        patent_number: str,
        year: int,
        payment_date: datetime,
        amount: Decimal
    ) -> bool:
        """
        Record annuity payment

        Args:
            patent_number: Patent number
            year: Annuity year
            payment_date: Payment date
            amount: Amount paid

        Returns:
            True if successful
        """
        if patent_number not in self.patents:
            logger.error(f"Patent {patent_number} not found")
            return False

        annuities = self.patents[patent_number]

        for fee in annuities.annuities:
            if fee.year == year:
                fee.paid = True
                fee.payment_date = payment_date

                # Check for late payment
                if payment_date > fee.due_date:
                    days_late = (payment_date - fee.due_date).days
                    fee.late_payment_fee = self._calculate_late_fee(
                        fee.amount,
                        days_late,
                        annuities.jurisdiction
                    )

                logger.info(f"Recorded payment for patent {patent_number} year {year}")
                return True

        logger.warning(f"Annuity year {year} not found for patent {patent_number}")
        return False

    def get_upcoming_payments(
        self,
        days_ahead: int = 90
    ) -> List[Tuple[str, AnnuityFee]]:
        """
        Get upcoming annuity payments

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of (patent_number, fee) tuples
        """
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        upcoming = []

        for patent_number, annuities in self.patents.items():
            for fee in annuities.annuities:
                if not fee.paid and now <= fee.due_date <= future:
                    upcoming.append((patent_number, fee))

        # Sort by due date
        upcoming.sort(key=lambda x: x[1].due_date)

        return upcoming

    def get_overdue_payments(self) -> List[Tuple[str, AnnuityFee]]:
        """Get overdue annuity payments"""
        now = datetime.now()
        overdue = []

        for patent_number, annuities in self.patents.items():
            for fee in annuities.annuities:
                if not fee.paid and fee.due_date < now:
                    overdue.append((patent_number, fee))

        return overdue

    def calculate_portfolio_cost(self) -> Dict[str, any]:
        """Calculate total portfolio cost"""
        total_cost = Decimal("0.00")
        paid_cost = Decimal("0.00")
        outstanding_cost = Decimal("0.00")

        for annuities in self.patents.values():
            for fee in annuities.annuities:
                total_cost += fee.amount
                if fee.paid:
                    paid_cost += fee.amount
                else:
                    outstanding_cost += fee.amount

        return {
            "total_cost": float(total_cost),
            "paid_cost": float(paid_cost),
            "outstanding_cost": float(outstanding_cost),
            "patents_count": len(self.patents),
            "paid_percentage": float(paid_cost / total_cost * 100) if total_cost > 0 else 0
        }

    def get_patent_status(self, patent_number: str) -> Dict[str, any]:
        """Get payment status for a patent"""
        if patent_number not in self.patents:
            return {"error": "Patent not found"}

        annuities = self.patents[patent_number]

        return {
            "patent_number": patent_number,
            "jurisdiction": annuities.jurisdiction,
            "issue_date": annuities.issue_date.isoformat(),
            "expiration_date": annuities.expiration_date.isoformat(),
            "total_cost": float(annuities.total_cost),
            "paid_count": sum(1 for f in annuities.annuities if f.paid),
            "total_annuities": len(annuities.annuities),
            "status": annuities.maintenance_status,
            "annuities": [
                {
                    "year": f.year,
                    "amount": float(f.amount),
                    "due_date": f.due_date.isoformat(),
                    "paid": f.paid,
                    "payment_date": f.payment_date.isoformat() if f.payment_date else None
                }
                for f in annuities.annuities
            ]
        }

    def _calculate_late_fee(
        self,
        base_amount: Decimal,
        days_late: int,
        jurisdiction: str
    ) -> Decimal:
        """Calculate late payment fee"""
        # Simplified late fee calculation
        if days_late <= 30:
            return base_amount * Decimal("0.25")
        elif days_late <= 90:
            return base_amount * Decimal("0.50")
        else:
            return base_amount * Decimal("1.00")


class AnnuityReport:
    """Generate annuity reports"""

    def __init__(self, tracker: AnnuityTracker):
        """
        Initialize report

        Args:
            tracker: AnnuityTracker instance
        """
        self.tracker = tracker

    def generate_summary(self) -> str:
        """Generate summary report"""
        portfolio = self.tracker.calculate_portfolio_cost()

        report = "ANNUITY PAYMENT REPORT\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Portfolio Summary:\n"
        report += f"- Patents: {portfolio['patents_count']}\n"
        report += f"- Total Cost: ${portfolio['total_cost']:,.2f}\n"
        report += f"- Paid: ${portfolio['paid_cost']:,.2f}\n"
        report += f"- Outstanding: ${portfolio['outstanding_cost']:,.2f}\n"
        report += f"- Paid %: {portfolio['paid_percentage']:.1f}%\n\n"

        upcoming = self.tracker.get_upcoming_payments(days_ahead=90)
        if upcoming:
            report += "Upcoming Payments (next 90 days):\n"
            for patent, fee in upcoming[:5]:
                report += f"- {patent} (Year {fee.year}): ${fee.amount} due {fee.due_date.strftime('%Y-%m-%d')}\n"

        return report

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        portfolio = self.tracker.calculate_portfolio_cost()

        return {
            "generated": datetime.now().isoformat(),
            "portfolio": portfolio,
            "upcoming_payments": [
                {
                    "patent": p,
                    "year": f.year,
                    "amount": float(f.amount),
                    "due_date": f.due_date.isoformat()
                }
                for p, f in self.tracker.get_upcoming_payments(days_ahead=90)
            ]
        }


def main():
    """Example usage"""
    calculator = AnnuityCalculator()
    tracker = AnnuityTracker(calculator)

    # Add patents
    issue_date = datetime(2021, 6, 15)
    tracker.add_patent("10000000", issue_date, "US")
    tracker.add_patent("10000001", issue_date, "EP")

    # Record a payment
    tracker.record_payment("10000000", 3, datetime(2024, 6, 15), Decimal("1600"))

    # Get portfolio summary
    portfolio = tracker.calculate_portfolio_cost()
    print(f"Portfolio Cost Summary:")
    print(f"  Total: ${portfolio['total_cost']:,.2f}")
    print(f"  Paid: ${portfolio['paid_cost']:,.2f}")
    print(f"  Outstanding: ${portfolio['outstanding_cost']:,.2f}")

    # Generate report
    report = AnnuityReport(tracker)
    print("\n" + report.generate_summary())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
