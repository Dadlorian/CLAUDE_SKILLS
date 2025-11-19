// Telehealth appointment scheduling API
const express = require('express');
const router = express.Router();

router.post('/appointments', async (req, res) => {
  const { patientId, providerId, scheduledTime, duration, visitReason } = req.body;

  try {
    // Check provider availability
    const conflicts = await db.query(`
      SELECT * FROM appointments
      WHERE provider_id = $1 AND status != 'cancelled'
      AND tsrange(scheduled_time, scheduled_time + (duration_minutes || ' minutes')::INTERVAL)
      && tsrange($2::timestamp, $2::timestamp + ($3 || ' minutes')::INTERVAL)
    `, [providerId, scheduledTime, duration]);

    if (conflicts.rows.length > 0) {
      return res.status(400).json({ error: 'Time slot not available' });
    }

    // Create video room
    const videoRoom = await createVideoRoom(patientId, providerId);

    // Create appointment
    const result = await db.query(`
      INSERT INTO appointments
      (patient_id, provider_id, scheduled_time, duration_minutes, visit_reason, video_room_url, status)
      VALUES ($1, $2, $3, $4, $5, $6, 'scheduled')
      RETURNING *
    `, [patientId, providerId, scheduledTime, duration, visitReason, videoRoom.url]);

    // Send confirmations
    await sendAppointmentConfirmation(result.rows[0]);

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Scheduling error:', error);
    res.status(500).json({ error: 'Failed to schedule appointment' });
  }
});

module.exports = router;
