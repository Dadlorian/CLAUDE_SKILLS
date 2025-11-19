/**
 * Patient Appointment Scheduling System
 * Manages appointment scheduling, rescheduling, and reminders
 */

import React, { useState, useEffect } from 'react';

const AppointmentScheduler = ({ patientId }) => {
  const [appointments, setAppointments] = useState([]);
  const [providers, setProviders] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [showScheduler, setShowScheduler] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);

  useEffect(() => {
    fetchAppointments();
    fetchProviders();
  }, [patientId]);

  const fetchAppointments = async () => {
    const response = await fetch(`/api/patients/${patientId}/appointments`);
    const data = await response.json();
    setAppointments(data.appointments);
  };

  const fetchProviders = async () => {
    const response = await fetch('/api/providers');
    const data = await response.json();
    setProviders(data.providers);
  };

  const fetchAvailableSlots = async (providerId, date) => {
    const response = await fetch(
      `/api/providers/${providerId}/availability?date=${date}`
    );
    const data = await response.json();
    setAvailableSlots(data.slots);
  };

  const handleProviderSelect = (provider) => {
    setSelectedProvider(provider);
    if (selectedDate) {
      fetchAvailableSlots(provider.id, selectedDate);
    }
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    if (selectedProvider) {
      fetchAvailableSlots(selectedProvider.id, date);
    }
  };

  const scheduleAppointment = async () => {
    const appointment = {
      provider_id: selectedProvider.id,
      appointment_date: selectedDate,
      appointment_time: selectedTime,
      reason: 'Patient scheduled'
    };

    const response = await fetch(
      `/api/patients/${patientId}/appointments`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appointment)
      }
    );

    if (response.ok) {
      await fetchAppointments();
      setShowScheduler(false);
      resetForm();
    }
  };

  const cancelAppointment = async (appointmentId) => {
    const response = await fetch(
      `/api/appointments/${appointmentId}`,
      { method: 'DELETE' }
    );

    if (response.ok) {
      fetchAppointments();
    }
  };

  const rescheduleAppointment = async (appointmentId) => {
    setShowScheduler(true);
    // Load appointment details for rescheduling
  };

  const resetForm = () => {
    setSelectedProvider(null);
    setSelectedDate(null);
    setSelectedTime(null);
  };

  const upcomingAppointments = appointments.filter(
    a => new Date(a.appointment_date) >= new Date()
  );

  const pastAppointments = appointments.filter(
    a => new Date(a.appointment_date) < new Date()
  );

  return (
    <div className="appointment-scheduler">
      <h2>Your Appointments</h2>

      <div className="appointments-section">
        <h3>Upcoming Appointments ({upcomingAppointments.length})</h3>
        {upcomingAppointments.length === 0 ? (
          <p>No upcoming appointments</p>
        ) : (
          <div className="appointment-list">
            {upcomingAppointments.map(apt => (
              <AppointmentCard
                key={apt.id}
                appointment={apt}
                onCancel={() => cancelAppointment(apt.id)}
                onReschedule={() => rescheduleAppointment(apt.id)}
              />
            ))}
          </div>
        )}

        <button
          className="primary"
          onClick={() => {
            resetForm();
            setShowScheduler(!showScheduler);
          }}
        >
          {showScheduler ? 'Cancel' : 'Schedule New Appointment'}
        </button>
      </div>

      {showScheduler && (
        <SchedulingForm
          providers={providers}
          selectedProvider={selectedProvider}
          onProviderSelect={handleProviderSelect}
          selectedDate={selectedDate}
          onDateSelect={handleDateSelect}
          availableSlots={availableSlots}
          selectedTime={selectedTime}
          onTimeSelect={setSelectedTime}
          onSchedule={scheduleAppointment}
        />
      )}

      <div className="past-appointments">
        <h3>Past Appointments</h3>
        {pastAppointments.slice(0, 3).map(apt => (
          <div key={apt.id} className="past-appointment">
            <p><strong>{apt.provider_name}</strong> - {new Date(apt.appointment_date).toLocaleDateString()}</p>
            <p>{apt.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const AppointmentCard = ({ appointment, onCancel, onReschedule }) => {
  const appointmentDate = new Date(appointment.appointment_date);
  const isToday = appointmentDate.toDateString() === new Date().toDateString();
  const isTomorrow = appointmentDate.toDateString() === new Date(Date.now() + 86400000).toDateString();

  let dateLabel = appointmentDate.toLocaleDateString();
  if (isToday) dateLabel = 'Today';
  if (isTomorrow) dateLabel = 'Tomorrow';

  return (
    <div className="appointment-card">
      <div className="appointment-info">
        <h4>{appointment.provider_name}</h4>
        <p className="specialty">{appointment.specialty}</p>
        <div className="details">
          <p><strong>{dateLabel}</strong> at {appointment.appointment_time}</p>
          <p>{appointment.location}</p>
          <p>Phone: {appointment.phone}</p>
        </div>
      </div>

      <div className="appointment-actions">
        <button className="secondary" onClick={onReschedule}>
          Reschedule
        </button>
        <button className="danger" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
};

const SchedulingForm = ({
  providers,
  selectedProvider,
  onProviderSelect,
  selectedDate,
  onDateSelect,
  availableSlots,
  selectedTime,
  onTimeSelect,
  onSchedule
}) => {
  return (
    <div className="scheduling-form">
      <h3>Schedule an Appointment</h3>

      <div className="form-section">
        <label>Select a Provider</label>
        <div className="provider-selection">
          {providers.map(provider => (
            <div
              key={provider.id}
              className={`provider-option ${selectedProvider?.id === provider.id ? 'selected' : ''}`}
              onClick={() => onProviderSelect(provider)}
            >
              <strong>{provider.name}</strong>
              <p>{provider.specialty}</p>
            </div>
          ))}
        </div>
      </div>

      {selectedProvider && (
        <>
          <div className="form-section">
            <label>Select a Date</label>
            <input
              type="date"
              min={new Date().toISOString().split('T')[0]}
              value={selectedDate || ''}
              onChange={(e) => onDateSelect(e.target.value)}
            />
          </div>

          {selectedDate && availableSlots.length > 0 && (
            <div className="form-section">
              <label>Select a Time</label>
              <div className="time-slots">
                {availableSlots.map((slot, i) => (
                  <button
                    key={i}
                    className={`time-slot ${selectedTime === slot ? 'selected' : ''}`}
                    onClick={() => onTimeSelect(slot)}
                  >
                    {slot}
                  </button>
                ))}
              </div>
            </div>
          )}

          <button
            className="primary"
            disabled={!selectedTime}
            onClick={onSchedule}
          >
            Confirm Appointment
          </button>
        </>
      )}
    </div>
  );
};

export default AppointmentScheduler;
