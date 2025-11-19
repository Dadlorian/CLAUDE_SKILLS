using UnityEngine;

/// <summary>
/// Realistic vehicle controller with suspension, tire friction, and aerodynamics.
/// Based on real-world vehicle physics for arcade-realistic feel.
/// </summary>
[RequireComponent(typeof(Rigidbody))]
public class VehicleController : MonoBehaviour
{
    [System.Serializable]
    public class Wheel
    {
        public Transform wheelTransform;
        public WheelCollider wheelCollider;
        public bool isPowered = true;
        public bool canSteer = false;

        [HideInInspector] public WheelHit hit;
        [HideInInspector] public bool isGrounded;
    }

    #region Serialized Fields

    [Header("Wheels")]
    [SerializeField] private Wheel[] wheels;

    [Header("Engine")]
    [SerializeField] private float maxMotorTorque = 1500f;
    [SerializeField] private float maxSpeed = 50f; // m/s
    [SerializeField] private AnimationCurve enginePowerCurve = AnimationCurve.Linear(0, 1, 1, 0.5f);

    [Header("Steering")]
    [SerializeField] private float maxSteerAngle = 30f;
    [SerializeField] private float steerSpeed = 5f;

    [Header("Braking")]
    [SerializeField] private float brakeTorque = 3000f;
    [SerializeField] private float handbrakeTorque = 5000f;

    [Header("Suspension")]
    [SerializeField] private float suspensionDistance = 0.3f;
    [SerializeField] private float suspensionSpring = 35000f;
    [SerializeField] private float suspensionDamper = 4500f;

    [Header("Center of Mass")]
    [SerializeField] private Vector3 centerOfMassOffset = new Vector3(0, -0.5f, 0);

    [Header("Aerodynamics")]
    [SerializeField] private float downforceCoefficient = 2f;
    [SerializeField] private float dragCoefficient = 0.3f;

    [Header("Tire Friction")]
    [SerializeField] private float forwardStiffness = 1.5f;
    [SerializeField] private float sidewaysStiffness = 1.5f;

    #endregion

    #region Private Fields

    private Rigidbody rb;
    private float currentSteerAngle;
    private float currentSpeed;
    private float motorInput;
    private float steerInput;
    private bool isBraking;
    private bool isHandbraking;

    #endregion

    #region Unity Lifecycle

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();

        // Set center of mass lower for stability
        rb.centerOfMass = centerOfMassOffset;

        // Configure wheel colliders
        SetupWheels();
    }

    private void Update()
    {
        HandleInput();
        UpdateWheelVisuals();
    }

    private void FixedUpdate()
    {
        UpdateWheelPhysics();
        ApplyMotor();
        ApplySteering();
        ApplyBraking();
        ApplyAerodynamics();

        currentSpeed = rb.velocity.magnitude;
    }

    #endregion

    #region Setup

    private void SetupWheels()
    {
        foreach (Wheel wheel in wheels)
        {
            if (wheel.wheelCollider == null)
            {
                Debug.LogError($"Wheel collider not assigned for {wheel.wheelTransform.name}");
                continue;
            }

            // Configure suspension
            JointSpring spring = wheel.wheelCollider.suspensionSpring;
            spring.spring = suspensionSpring;
            spring.damper = suspensionDamper;
            spring.targetPosition = 0.5f;
            wheel.wheelCollider.suspensionSpring = spring;
            wheel.wheelCollider.suspensionDistance = suspensionDistance;

            // Configure tire friction
            WheelFrictionCurve forwardFriction = wheel.wheelCollider.forwardFriction;
            forwardFriction.stiffness = forwardStiffness;
            wheel.wheelCollider.forwardFriction = forwardFriction;

            WheelFrictionCurve sidewaysFriction = wheel.wheelCollider.sidewaysFriction;
            sidewaysFriction.stiffness = sidewaysStiffness;
            wheel.wheelCollider.sidewaysFriction = sidewaysFriction;
        }
    }

    #endregion

    #region Input

    private void HandleInput()
    {
        motorInput = Input.GetAxis("Vertical");
        steerInput = Input.GetAxis("Horizontal");
        isBraking = Input.GetKey(KeyCode.Space);
        isHandbraking = Input.GetKey(KeyCode.LeftShift);
    }

    #endregion

    #region Physics

    private void UpdateWheelPhysics()
    {
        foreach (Wheel wheel in wheels)
        {
            wheel.isGrounded = wheel.wheelCollider.GetGroundHit(out wheel.hit);
        }
    }

    private void ApplyMotor()
    {
        if (currentSpeed >= maxSpeed && motorInput > 0)
            return; // Speed limiter

        // Calculate motor torque based on engine curve
        float speedRatio = currentSpeed / maxSpeed;
        float enginePower = enginePowerCurve.Evaluate(speedRatio);
        float torque = motorInput * maxMotorTorque * enginePower;

        // Apply to powered wheels
        foreach (Wheel wheel in wheels)
        {
            if (wheel.isPowered)
            {
                wheel.wheelCollider.motorTorque = torque;
            }
        }
    }

    private void ApplySteering()
    {
        // Smooth steering
        float targetSteerAngle = steerInput * maxSteerAngle;
        currentSteerAngle = Mathf.Lerp(currentSteerAngle, targetSteerAngle, Time.fixedDeltaTime * steerSpeed);

        // Apply to steerable wheels
        foreach (Wheel wheel in wheels)
        {
            if (wheel.canSteer)
            {
                wheel.wheelCollider.steerAngle = currentSteerAngle;
            }
        }
    }

    private void ApplyBraking()
    {
        float brake = 0f;

        if (isBraking)
        {
            brake = brakeTorque;
        }
        else if (isHandbraking)
        {
            brake = handbrakeTorque;
        }

        foreach (Wheel wheel in wheels)
        {
            // Handbrake only affects rear wheels (example: indices 2, 3)
            if (isHandbraking && !wheel.isPowered)
            {
                wheel.wheelCollider.brakeTorque = brake;
            }
            else if (isBraking)
            {
                wheel.wheelCollider.brakeTorque = brake;
            }
            else
            {
                wheel.wheelCollider.brakeTorque = 0f;
            }
        }
    }

    private void ApplyAerodynamics()
    {
        // Downforce (increases with speed squared)
        float downforce = downforceCoefficient * currentSpeed * currentSpeed;
        rb.AddForce(-transform.up * downforce);

        // Air drag
        float drag = dragCoefficient * currentSpeed * currentSpeed;
        rb.AddForce(-rb.velocity.normalized * drag);
    }

    #endregion

    #region Visuals

    private void UpdateWheelVisuals()
    {
        foreach (Wheel wheel in wheels)
        {
            if (wheel.wheelTransform == null)
                continue;

            // Get wheel position and rotation from collider
            Vector3 position;
            Quaternion rotation;
            wheel.wheelCollider.GetWorldPose(out position, out rotation);

            // Apply to visual wheel
            wheel.wheelTransform.position = position;
            wheel.wheelTransform.rotation = rotation;
        }
    }

    #endregion

    #region Public API

    /// <summary>
    /// Get current speed in km/h
    /// </summary>
    public float GetSpeedKmh()
    {
        return currentSpeed * 3.6f;
    }

    /// <summary>
    /// Get current RPM (simplified)
    /// </summary>
    public float GetRPM()
    {
        // Simplified RPM calculation
        float wheelRPM = 0f;
        int poweredWheelCount = 0;

        foreach (Wheel wheel in wheels)
        {
            if (wheel.isPowered)
            {
                wheelRPM += wheel.wheelCollider.rpm;
                poweredWheelCount++;
            }
        }

        if (poweredWheelCount > 0)
            wheelRPM /= poweredWheelCount;

        // Gear ratio approximation (5th gear ~= 3.5:1, final drive ~= 3.5:1)
        float engineRPM = Mathf.Abs(wheelRPM) * 3.5f * 3.5f;

        return Mathf.Clamp(engineRPM, 800f, 7000f); // Idle to redline
    }

    /// <summary>
    /// Check if any wheel is grounded
    /// </summary>
    public bool IsGrounded()
    {
        foreach (Wheel wheel in wheels)
        {
            if (wheel.isGrounded)
                return true;
        }
        return false;
    }

    /// <summary>
    /// Get slip angle (for drifting detection)
    /// </summary>
    public float GetSlipAngle()
    {
        float totalSlip = 0f;
        int wheelCount = 0;

        foreach (Wheel wheel in wheels)
        {
            if (wheel.isGrounded)
            {
                totalSlip += Mathf.Abs(wheel.hit.sidewaysSlip);
                wheelCount++;
            }
        }

        return wheelCount > 0 ? totalSlip / wheelCount : 0f;
    }

    #endregion

    #region Debug

    private void OnDrawGizmos()
    {
        if (!Application.isPlaying || rb == null)
            return;

        // Draw center of mass
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(rb.worldCenterOfMass, 0.1f);

        // Draw velocity vector
        Gizmos.color = Color.blue;
        Gizmos.DrawRay(transform.position, rb.velocity);

        // Draw wheel ground contacts
        foreach (Wheel wheel in wheels)
        {
            if (wheel.isGrounded)
            {
                Gizmos.color = Color.green;
                Gizmos.DrawSphere(wheel.hit.point, 0.05f);
            }
        }
    }

    #endregion
}
