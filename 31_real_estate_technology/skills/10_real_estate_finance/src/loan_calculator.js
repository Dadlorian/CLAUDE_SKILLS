/**
 * Mortgage Loan Calculator
 */
class LoanCalculator {
  constructor(principal, rate, years) {
    this.principal = principal;
    this.rate = rate / 100;  // Convert to decimal
    this.years = years;
  }
  
  calculateMonthlyPayment() {
    const monthlyRate = this.rate / 12;
    const nPayments = this.years * 12;
    
    const payment = this.principal * (
      monthlyRate * Math.pow(1 + monthlyRate, nPayments)
    ) / (Math.pow(1 + monthlyRate, nPayments) - 1);
    
    return Math.round(payment * 100) / 100;
  }
  
  calculateTotalInterest() {
    const monthlyPayment = this.calculateMonthlyPayment();
    const totalPaid = monthlyPayment * this.years * 12;
    return Math.round((totalPaid - this.principal) * 100) / 100;
  }
  
  generateAmortizationSchedule() {
    const schedule = [];
    let balance = this.principal;
    const monthlyPayment = this.calculateMonthlyPayment();
    const monthlyRate = this.rate / 12;
    
    for (let month = 1; month <= this.years * 12; month++) {
      const interestPayment = balance * monthlyRate;
      const principalPayment = monthlyPayment - interestPayment;
      balance -= principalPayment;
      
      schedule.push({
        month,
        payment: monthlyPayment,
        principal: principalPayment,
        interest: interestPayment,
        balance: Math.max(0, balance)
      });
    }
    
    return schedule;
  }
}

module.exports = LoanCalculator;
