/**
 * Rent Calculator
 */
class RentCalculator {
  constructor(baseRent) {
    this.baseRent = baseRent;
  }
  
  calculateProrated(daysOccupied, daysInMonth) {
    const dailyRent = this.baseRent / daysInMonth;
    return Math.round(dailyRent * daysOccupied * 100) / 100;
  }
  
  calculateLateFee(rentAmount, lateDays) {
    if (lateDays <= 0) return 0;
    
    // $50 or 5%, whichever is greater
    const percentageFee = rentAmount * 0.05;
    return Math.max(50, percentageFee);
  }
  
  calculateEscalation(yearNumber, escalationType = 'fixed', escalationRate = 0.03) {
    if (escalationType === 'fixed') {
      return this.baseRent * Math.pow(1 + escalationRate, yearNumber - 1);
    } else if (escalationType === 'cpi') {
      // CPI-based escalation (simplified)
      return this.baseRent * (1 + escalationRate);
    }
    return this.baseRent;
  }
  
  calculateAnnualRent(escalations = []) {
    let total = 0;
    escalations.forEach((rate, index) => {
      total += this.calculateEscalation(index + 1, 'fixed', rate) * 12;
    });
    return total;
  }
}

module.exports = RentCalculator;
