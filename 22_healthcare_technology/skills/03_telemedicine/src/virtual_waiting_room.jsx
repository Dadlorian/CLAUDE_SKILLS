/**
 * Virtual Waiting Room Component
 * React component for telehealth virtual waiting room
 */

import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Clock, Video } from 'lucide-react';

const VirtualWaitingRoom = ({ appointmentId, patientName, providerName, scheduledTime }) => {
  const [systemCheck, setSystemCheck] = useState({ camera: null, microphone: null, internet: null });
  const [waitTime, setWaitTime] = useState(null);
  const [status, setStatus] = useState('waiting'); // waiting, ready, admitted

  useEffect(() => {
    runSystemCheck();
    estimateWaitTime();
    
    const interval = setInterval(() => {
      checkAdmissionStatus();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const runSystemCheck = async () => {
    // Check camera
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setSystemCheck(prev => ({ ...prev, camera: true }));
      stream.getTracks().forEach(track => track.stop());
    } catch (err) {
      setSystemCheck(prev => ({ ...prev, camera: false }));
    }

    // Check microphone
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true }));
      setSystemCheck(prev => ({ ...prev, microphone: true }));
      stream.getTracks().forEach(track => track.stop());
    } catch (err) {
      setSystemCheck(prev => ({ ...prev, microphone: false }));
    }

    // Check internet speed
    const startTime = Date.now();
    try {
      await fetch('https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png');
      const duration = Date.now() - startTime;
      setSystemCheck(prev => ({ ...prev, internet: duration < 2000 }));
    } catch (err) {
      setSystemCheck(prev => ({ ...prev, internet: false }));
    }
  };

  const estimateWaitTime = async () => {
    const response = await fetch(`/api/appointments/${appointmentId}/wait-time`);
    const data = await response.json();
    setWaitTime(data.estimatedMinutes);
  };

  const checkAdmissionStatus = async () => {
    const response = await fetch(`/api/appointments/${appointmentId}/status`);
    const data = await response.json();
    if (data.status === 'admitted') {
      setStatus('admitted');
      window.location.href = data.videoUrl;
    }
  };

  const SystemCheckItem = ({ label, status }) => (
    <div className="flex items-center space-x-2 py-2">
      {status === true && <CheckCircle className="text-green-500" size={20} />}
      {status === false && <AlertCircle className="text-red-500" size={20} />}
      {status === null && <Clock className="text-gray-400" size={20} />}
      <span className={status === false ? 'text-red-600' : ''}>{label}</span>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="text-center mb-8">
        <Video className="mx-auto mb-4 text-blue-600" size={48} />
        <h1 className="text-2xl font-bold mb-2">Welcome to Your Telehealth Visit</h1>
        <p className="text-gray-600">
          Dr. {providerName} will be with you shortly
        </p>
      </div>

      <div className="bg-blue-50 rounded-lg p-6 mb-6">
        <h2 className="font-semibold mb-4">System Check</h2>
        <SystemCheckItem label="Camera" status={systemCheck.camera} />
        <SystemCheckItem label="Microphone" status={systemCheck.microphone} />
        <SystemCheckItem label="Internet Connection" status={systemCheck.internet} />
      </div>

      {waitTime !== null && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-center text-yellow-800">
            <Clock className="inline mr-2" size={16} />
            Estimated wait time: <strong>{waitTime} minutes</strong>
          </p>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold mb-3">While you wait:</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• Make sure you're in a quiet, private location</li>
          <li>• Have your medication list ready</li>
          <li>• Prepare any questions you'd like to ask</li>
          <li>• Keep your insurance card handy</li>
        </ul>
      </div>

      <div className="mt-6 text-center text-sm text-gray-500">
        <p>Need help? <a href="/support" className="text-blue-600 underline">Contact support</a></p>
      </div>
    </div>
  );
};

export default VirtualWaitingRoom;
