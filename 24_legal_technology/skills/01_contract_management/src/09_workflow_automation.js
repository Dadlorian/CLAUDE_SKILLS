/**
 * Workflow Automation - Automate contract approval and management workflows
 * Node.js implementation using workflow engine
 */

const EventEmitter = require('events');

class WorkflowStep {
  constructor(stepName, approvers, escalationTime = 48) {
    this.stepName = stepName;
    this.approvers = approvers; // Array of approver emails
    this.escalationTime = escalationTime; // hours
    this.status = 'pending';
    this.completedAt = null;
  }
}

class ContractWorkflow extends EventEmitter {
  constructor(contractId, contractData) {
    super();
    this.contractId = contractId;
    this.contractData = contractData;
    this.steps = [];
    this.currentStepIndex = 0;
    this.startedAt = new Date();
    this.status = 'in_progress';
  }

  addStep(stepName, approvers, escalationTime = 48) {
    const step = new WorkflowStep(stepName, approvers, escalationTime);
    this.steps.push(step);
    return this;
  }

  async executeStep(stepIndex) {
    if (stepIndex >= this.steps.length) {
      this.completeWorkflow();
      return;
    }

    const step = this.steps[stepIndex];
    console.log(`Executing step: ${step.stepName}`);

    // Send approval notifications
    await this.notifyApprovers(step);

    // Set escalation timer
    this.setEscalationTimer(step, stepIndex);

    // Emit step started event
    this.emit('stepStarted', {
      contractId: this.contractId,
      step: step.stepName,
      approvers: step.approvers,
      startTime: new Date()
    });
  }

  async notifyApprovers(step) {
    const notifications = step.approvers.map(approver => ({
      to: approver,
      subject: `Contract Approval Required: ${this.contractData.title}`,
      body: `Contract ${this.contractId} is awaiting your approval.`,
      contractId: this.contractId,
      action: 'approve'
    }));

    for (const notification of notifications) {
      await this.sendNotification(notification);
    }
  }

  async sendNotification(notification) {
    // Implementation would use email service (SendGrid, etc.)
    console.log(`Notification sent to ${notification.to}`);
    // Emit event for logging
    this.emit('notificationSent', notification);
  }

  setEscalationTimer(step, stepIndex) {
    const escalationMs = step.escalationTime * 60 * 60 * 1000;

    setTimeout(() => {
      if (step.status === 'pending') {
        this.escalateApproval(step, stepIndex);
      }
    }, escalationMs);
  }

  escalateApproval(step, stepIndex) {
    console.log(`Escalating approval for step: ${step.stepName}`);

    // Notify management
    this.emit('escalated', {
      contractId: this.contractId,
      step: step.stepName,
      escalatedAt: new Date(),
      approvers: step.approvers
    });

    // Send escalation email
    const escalationEmail = {
      to: 'management@company.com',
      subject: `URGENT: Contract Approval Escalation - ${this.contractId}`,
      body: `Contract is overdue for approval. Please review immediately.`,
      contractId: this.contractId
    };

    this.sendNotification(escalationEmail);
  }

  async approveStep(stepIndex, approverId, comments = '') {
    const step = this.steps[stepIndex];
    step.status = 'approved';
    step.completedAt = new Date();
    step.approvedBy = approverId;
    step.comments = comments;

    console.log(`Step ${step.stepName} approved by ${approverId}`);

    this.emit('stepApproved', {
      contractId: this.contractId,
      step: step.stepName,
      approvedBy: approverId,
      approvedAt: new Date()
    });

    // Execute next step
    if (stepIndex + 1 < this.steps.length) {
      this.currentStepIndex = stepIndex + 1;
      await this.executeStep(this.currentStepIndex);
    } else {
      this.completeWorkflow();
    }
  }

  async rejectStep(stepIndex, rejectorId, reason = '') {
    const step = this.steps[stepIndex];
    step.status = 'rejected';
    step.rejectedBy = rejectorId;
    step.rejectionReason = reason;

    console.log(`Step ${step.stepName} rejected by ${rejectorId}`);

    this.emit('stepRejected', {
      contractId: this.contractId,
      step: step.stepName,
      rejectedBy: rejectorId,
      reason: reason,
      rejectedAt: new Date()
    });

    // Reset to first step or notify
    this.currentStepIndex = 0;
    this.status = 'rejected';
  }

  completeWorkflow() {
    this.status = 'completed';
    const completionTime = new Date() - this.startedAt;

    console.log(`Workflow completed in ${completionTime}ms`);

    this.emit('workflowCompleted', {
      contractId: this.contractId,
      completedAt: new Date(),
      duration: completionTime,
      steps: this.steps.map(s => ({
        name: s.stepName,
        status: s.status,
        approvedBy: s.approvedBy,
        completedAt: s.completedAt
      }))
    });
  }

  getStatus() {
    return {
      contractId: this.contractId,
      status: this.status,
      currentStep: this.currentStepIndex < this.steps.length ? this.steps[this.currentStepIndex].stepName : null,
      progress: `${this.currentStepIndex}/${this.steps.length}`,
      steps: this.steps.map(s => ({
        name: s.stepName,
        status: s.status,
        completedAt: s.completedAt
      }))
    };
  }
}

module.exports = { ContractWorkflow, WorkflowStep };

// Example usage
if (require.main === module) {
  const workflow = new ContractWorkflow('CNT-2024-001', {
    title: 'Service Agreement with Acme Corp'
  });

  workflow
    .addStep('Legal Review', ['legal@company.com'], 24)
    .addStep('Finance Review', ['finance@company.com'], 24)
    .addStep('Management Approval', ['manager@company.com'], 48);

  workflow.on('stepApproved', (data) => {
    console.log('Step approved:', data);
  });

  workflow.on('workflowCompleted', (data) => {
    console.log('Workflow completed:', data);
  });

  workflow.executeStep(0);
}
