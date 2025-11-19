using UnityEngine;
using Mirror;

/// <summary>
/// Optimized network transform with client prediction and interpolation.
/// </summary>
public class NetworkTransform : NetworkBehaviour
{
    [Header("Sync Settings")]
    [SerializeField] private bool syncPosition = true;
    [SerializeField] private bool syncRotation = true;
    [SerializeField] private float positionThreshold = 0.01f;
    [SerializeField] private float rotationThreshold = 1f;

    [Header("Interpolation")]
    [SerializeField] private float interpolationSpeed = 15f;

    [SyncVar] private Vector3 syncPosition;
    [SyncVar] private Quaternion syncRotation;

    private Vector3 lastPosition;
    private Quaternion lastRotation;
    private float lastSyncTime;

    private void Update()
    {
        if (isServer)
        {
            // Server updates SyncVars
            if (HasMoved())
            {
                syncPosition = transform.position;
                syncRotation = transform.rotation;
                lastPosition = transform.position;
                lastRotation = transform.rotation;
            }
        }
        else
        {
            // Clients interpolate to sync values
            if (syncPosition)
                transform.position = Vector3.Lerp(transform.position, syncPosition, Time.deltaTime * interpolationSpeed);

            if (syncRotation)
                transform.rotation = Quaternion.Slerp(transform.rotation, syncRotation, Time.deltaTime * interpolationSpeed);
        }
    }

    private bool HasMoved()
    {
        if (syncPosition && Vector3.Distance(transform.position, lastPosition) > positionThreshold)
            return true;

        if (syncRotation && Quaternion.Angle(transform.rotation, lastRotation) > rotationThreshold)
            return true;

        return false;
    }
}
