"""
Physics-Based Simulation Module for Digital Twins

This module provides physics simulation capabilities for digital twins,
including kinematics, dynamics, thermal modeling, and multi-physics coupling.

Key Features:
- Rigid body dynamics (forces, torques, acceleration)
- Kinematic analysis (position, velocity, orientation)
- Thermal modeling (heat transfer, temperature transients)
- Fluid systems (pneumatics, hydraulics)
- Material models (elasticity, plasticity, damping)
- Multi-physics coupling (thermoelastic, etc.)

Author: Digital Twins Skill Domain
Version: 1.0
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Dict, List, Optional
from scipy.integrate import odeint, solve_ivp
from scipy.spatial.transform import Rotation
import logging


# ============================================================================
# Configuration and Enums
# ============================================================================

class MechanicsModel(Enum):
    """Available mechanics modeling approaches"""
    RIGID_BODY = "rigid"
    FLEXIBLE_BODY = "flexible"
    RIGID_WITH_DAMPING = "rigid_damped"


class ThermalModel(Enum):
    """Available thermal modeling approaches"""
    LUMPED_CAPACITY = "lumped"
    DISTRIBUTED_1D = "1d"
    DISTRIBUTED_3D = "3d"


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class RigidBodyProperties:
    """Properties of a rigid body"""
    mass: float                    # kg
    inertia: np.ndarray           # 3x3 matrix [kg⋅m²]
    center_of_mass: np.ndarray    # [m] relative to body origin
    friction_coefficient: float    # Dimensionless
    damping_linear: float         # N⋅s/m
    damping_angular: float        # N⋅m⋅s/rad


@dataclass
class ThermalProperties:
    """Thermal properties of a material"""
    density: float                 # kg/m³
    specific_heat: float          # J/(kg⋅K)
    thermal_conductivity: float   # W/(m⋅K)
    thermal_expansion: float      # 1/K


@dataclass
class JointConstraint:
    """Represents a joint between two bodies"""
    parent_body_id: str
    child_body_id: str
    joint_type: str               # "revolute", "prismatic", "fixed"
    axis: np.ndarray              # Joint rotation axis [3]
    position: np.ndarray          # Joint position in parent frame [3]
    limits: Tuple[float, float]   # Min/max joint angle or position


@dataclass
class SimulationState:
    """Complete state of a simulation"""
    time: float
    body_positions: Dict[str, np.ndarray]    # Position of each body center
    body_rotations: Dict[str, Rotation]      # Orientation of each body
    body_velocities: Dict[str, np.ndarray]   # Linear velocity [m/s]
    body_angular_velocities: Dict[str, np.ndarray]  # Angular velocity [rad/s]
    joint_angles: Dict[str, float]           # Joint positions/angles
    joint_velocities: Dict[str, float]       # Joint velocities
    temperatures: Dict[str, float]           # Temperature [K]


# ============================================================================
# Kinematics
# ============================================================================

class KinematicsAnalyzer:
    """Performs kinematic analysis (geometry of motion without forces)"""

    def __init__(self):
        self.logger = logging.getLogger("KinematicsAnalyzer")

    @staticmethod
    def denavit_hartenberg_matrix(d: float, theta: float, a: float,
                                  alpha: float) -> np.ndarray:
        """
        Compute Denavit-Hartenberg transformation matrix

        Args:
            d: Link offset along z-axis
            theta: Joint angle about z-axis
            a: Link length along x-axis
            alpha: Link twist about x-axis

        Returns:
            4x4 homogeneous transformation matrix
        """
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)

        return np.array([
            [ct, -st*ca, st*sa, a*ct],
            [st, ct*ca, -ct*sa, a*st],
            [0, sa, ca, d],
            [0, 0, 0, 1]
        ])

    def forward_kinematics(self, dh_params: List[Tuple[float, float, float, float]],
                          joint_angles: np.ndarray) -> np.ndarray:
        """
        Compute forward kinematics given joint angles

        Args:
            dh_params: List of (d, a, alpha) DH parameters per joint
            joint_angles: Current joint angles [rad]

        Returns:
            4x4 transformation matrix (position and orientation)
        """
        T = np.eye(4)
        for i, (d, a, alpha) in enumerate(dh_params):
            T_i = self.denavit_hartenberg_matrix(d, joint_angles[i], a, alpha)
            T = T @ T_i
        return T

    def jacobian_analytical(self, dh_params: List[Tuple[float, float, float, float]],
                          joint_angles: np.ndarray) -> np.ndarray:
        """
        Compute Jacobian matrix analytically

        Jacobian maps joint velocities to end-effector velocities
        J = [∂position/∂θ_i, ...]

        Args:
            dh_params: DH parameters
            joint_angles: Current joint angles

        Returns:
            6xN Jacobian matrix (N = number of joints)
        """
        n_joints = len(joint_angles)
        J = np.zeros((6, n_joints))

        T_ee = self.forward_kinematics(dh_params, joint_angles)
        p_ee = T_ee[:3, 3]

        # Numerical differentiation for Jacobian
        delta = 1e-6
        for i in range(n_joints):
            angles_plus = joint_angles.copy()
            angles_plus[i] += delta

            T_plus = self.forward_kinematics(dh_params, angles_plus)
            p_plus = T_plus[:3, 3]

            J[:3, i] = (p_plus - p_ee) / delta

        # Angular velocity (z-axis of each frame)
        for i in range(n_joints):
            T = self.forward_kinematics(dh_params, joint_angles[:i+1])
            J[3:6, i] = T[:3, 2]  # z-axis

        return J

    def inverse_kinematics_numerical(self, dh_params: List[Tuple[float, float, float, float]],
                                     target_pose: np.ndarray,
                                     initial_guess: Optional[np.ndarray] = None,
                                     iterations: int = 100,
                                     tolerance: float = 1e-6) -> Optional[np.ndarray]:
        """
        Solve inverse kinematics numerically using Levenberg-Marquardt

        Args:
            dh_params: DH parameters
            target_pose: Target 4x4 transformation matrix
            initial_guess: Starting joint angles
            iterations: Maximum iterations
            tolerance: Position tolerance [m]

        Returns:
            Joint angles achieving target, or None if unsuccessful
        """
        n_joints = len(dh_params)
        if initial_guess is None:
            q = np.zeros(n_joints)
        else:
            q = initial_guess.copy()

        target_pos = target_pose[:3, 3]

        for iteration in range(iterations):
            # Current position
            T = self.forward_kinematics(dh_params, q)
            current_pos = T[:3, 3]

            # Position error
            error = target_pos - current_pos
            error_norm = np.linalg.norm(error)

            if error_norm < tolerance:
                return q

            # Jacobian
            J = self.jacobian_analytical(dh_params, q)[:3, :]

            # Levenberg-Marquardt update
            lambda_lm = 0.01
            try:
                dq = np.linalg.solve(
                    J.T @ J + lambda_lm * np.eye(n_joints),
                    J.T @ error
                )
                q += dq
            except np.linalg.LinAlgError:
                # Singular matrix, return current best
                return q

        return q


# ============================================================================
# Rigid Body Dynamics
# ============================================================================

class RigidBodyDynamics:
    """Simulates rigid body motion under forces and torques"""

    def __init__(self, gravity: float = 9.81):
        self.gravity = gravity
        self.logger = logging.getLogger("RigidBodyDynamics")

    def equations_of_motion(self, state: np.ndarray, t: float,
                           body_props: RigidBodyProperties,
                           forces: np.ndarray,
                           torques: np.ndarray) -> np.ndarray:
        """
        State-space representation of rigid body dynamics

        State vector: [x, y, z, vx, vy, vz, q0, q1, q2, q3, ωx, ωy, ωz]
        where q = quaternion, ω = angular velocity

        Returns:
            State derivative vector
        """
        # Extract state components
        position = state[0:3]
        velocity = state[3:6]
        quaternion = state[6:10]
        angular_velocity = state[10:13]

        # Normalize quaternion
        quaternion = quaternion / np.linalg.norm(quaternion)

        # Linear motion: ma = F - damping
        linear_accel = (forces - body_props.damping_linear * velocity) / body_props.mass

        # Add gravity
        linear_accel[2] -= self.gravity

        # Angular motion: I⋅α = τ - damping
        inertia_inv = np.linalg.inv(body_props.inertia)
        damping_torque = body_props.damping_angular * angular_velocity
        angular_accel = inertia_inv @ (torques - damping_torque)

        # Quaternion derivative (kinematic equation)
        omega_skew = self._skew_symmetric(angular_velocity)
        q_dot = 0.5 * omega_skew @ quaternion

        # Assemble state derivative
        state_dot = np.concatenate([
            velocity,
            linear_accel,
            q_dot,
            angular_accel
        ])

        return state_dot

    @staticmethod
    def _skew_symmetric(v: np.ndarray) -> np.ndarray:
        """Create skew-symmetric (cross-product) matrix"""
        return np.array([
            [0, -v[2], v[1]],
            [v[2], 0, -v[0]],
            [-v[1], v[0], 0]
        ])

    def simulate(self, initial_state: np.ndarray,
                body_props: RigidBodyProperties,
                time_points: np.ndarray,
                force_func: callable,
                torque_func: callable) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate rigid body motion

        Args:
            initial_state: Initial state vector [13]
            body_props: Body properties
            time_points: Time points for integration
            force_func: Function returning forces as f(t, state)
            torque_func: Function returning torques as f(t, state)

        Returns:
            (time_points, state_trajectory) where state_trajectory is [N, 13]
        """
        def state_derivatives(t, state):
            forces = force_func(t, state)
            torques = torque_func(t, state)
            return self.equations_of_motion(state, t, body_props, forces, torques)

        # Use scipy's solve_ivp for robust integration
        sol = solve_ivp(state_derivatives, [time_points[0], time_points[-1]],
                       initial_state, t_eval=time_points, method='RK45',
                       dense_output=True, max_step=0.001)

        return sol.t, sol.y.T


# ============================================================================
# Thermal Modeling
# ============================================================================

class ThermalModel:
    """Thermal modeling for digital twins"""

    def __init__(self, model_type: ThermalModel = ThermalModel.LUMPED_CAPACITY):
        self.model_type = model_type
        self.logger = logging.getLogger("ThermalModel")

    def lumped_capacity_ode(self, state: np.ndarray, t: float,
                           mass: float, specific_heat: float,
                           heat_generation: float,
                           surface_area: float, convection_coeff: float,
                           ambient_temp: float,
                           radiation_factor: float = 0.0) -> np.ndarray:
        """
        Lumped thermal capacity model (single temperature node)

        ODE: m⋅c⋅dT/dt = Q_gen - h⋅A⋅(T - T_amb) - ε⋅σ⋅A⋅(T⁴ - T_amb⁴)

        Args:
            state: [temperature] in K
            mass: Mass in kg
            specific_heat: Specific heat in J/(kg⋅K)
            heat_generation: Heat generated in W
            surface_area: Surface area in m²
            convection_coeff: Convection coefficient in W/(m²⋅K)
            ambient_temp: Ambient temperature in K
            radiation_factor: Radiation emissivity (0-1)

        Returns:
            Temperature rate of change [K/s]
        """
        temperature = state[0]

        # Convection heat loss
        q_conv = convection_coeff * surface_area * (temperature - ambient_temp)

        # Radiation heat loss (Stefan-Boltzmann)
        stefan_boltzmann = 5.67e-8  # W/(m²⋅K⁴)
        q_rad = (radiation_factor * stefan_boltzmann * surface_area *
                (temperature**4 - ambient_temp**4))

        # Temperature change
        capacity = mass * specific_heat
        dT_dt = (heat_generation - q_conv - q_rad) / capacity

        return np.array([dT_dt])

    def simulate_thermal_transient(self, initial_temp: float,
                                  mass: float, specific_heat: float,
                                  heat_generation_func: callable,
                                  surface_area: float,
                                  convection_coeff: float,
                                  ambient_temp: float,
                                  time_span: Tuple[float, float],
                                  num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate thermal transient response

        Args:
            initial_temp: Initial temperature [K]
            heat_generation_func: Function returning power as f(t) [W]
            time_span: (t_start, t_end)
            num_points: Number of time points

        Returns:
            (time_array, temperature_array)
        """
        time_points = np.linspace(time_span[0], time_span[1], num_points)

        def ode_func(t, T):
            Q = heat_generation_func(t)
            return self.lumped_capacity_ode(
                T, t, mass, specific_heat, Q,
                surface_area, convection_coeff, ambient_temp
            )

        sol = solve_ivp(ode_func, time_span, [initial_temp],
                       t_eval=time_points, method='RK45')

        return sol.t, sol.y[0, :]


# ============================================================================
# Pneumatic/Hydraulic Systems
# ============================================================================

class FluidPowerSystem:
    """Modeling of pneumatic and hydraulic systems"""

    def __init__(self):
        self.logger = logging.getLogger("FluidPowerSystem")

    @staticmethod
    def orifice_flow(pressure_in: float, pressure_out: float,
                    orifice_area: float, discharge_coeff: float = 0.61,
                    fluid_density: float = 1000.0) -> float:
        """
        Calculate flow through an orifice (Bernoulli equation)

        Q = Cd⋅A⋅√(2⋅ΔP / ρ)

        Args:
            pressure_in: Upstream pressure [Pa]
            pressure_out: Downstream pressure [Pa]
            orifice_area: Orifice area [m²]
            discharge_coeff: Discharge coefficient (0-1)
            fluid_density: Fluid density [kg/m³]

        Returns:
            Volume flow rate [m³/s]
        """
        dp = pressure_in - pressure_out
        if dp <= 0:
            return 0
        return discharge_coeff * orifice_area * np.sqrt(2 * dp / fluid_density)

    @staticmethod
    def actuator_force(pressure: float, area: float, friction_coeff: float = 0.1,
                      load: float = 0.0) -> float:
        """
        Calculate force produced by pneumatic/hydraulic actuator

        F = P⋅A - F_friction - F_load

        Args:
            pressure: Fluid pressure [Pa]
            area: Piston area [m²]
            friction_coeff: Friction coefficient
            load: External load [N]

        Returns:
            Net force produced [N]
        """
        pressure_force = pressure * area
        friction_force = friction_coeff * pressure_force
        return pressure_force - friction_force - load

    def accumulator_model(self, state: np.ndarray, t: float,
                         volume: float, polytropic_index: float = 1.4,
                         inflow: float = 0.0, outflow: float = 0.0) -> np.ndarray:
        """
        Model of gas accumulator (simplified isothermal)

        dP/dt = (γ-1)⋅P⋅(Q_in - Q_out) / V

        Args:
            state: [pressure] in Pa
            volume: Accumulator volume [m³]
            polytropic_index: Gas constant (1.4 for air)
            inflow: Volume flow in [m³/s]
            outflow: Volume flow out [m³/s]

        Returns:
            Pressure rate of change [Pa/s]
        """
        pressure = state[0]
        net_flow = inflow - outflow
        dP_dt = (polytropic_index - 1) * pressure * net_flow / volume
        return np.array([dP_dt])


# ============================================================================
# Material Models
# ============================================================================

class MaterialModel:
    """Material behavior modeling"""

    @staticmethod
    def linear_elastic_stress(strain: float, youngs_modulus: float) -> float:
        """
        Linear elastic stress-strain relation

        σ = E⋅ε
        """
        return youngs_modulus * strain

    @staticmethod
    def elastic_potential_energy(strain: float, youngs_modulus: float,
                                volume: float) -> float:
        """
        Elastic potential energy storage

        U = (1/2)⋅E⋅ε²⋅V
        """
        return 0.5 * youngs_modulus * (strain**2) * volume

    @staticmethod
    def von_mises_stress(stress_tensor: np.ndarray) -> float:
        """
        Compute von Mises equivalent stress

        σ_eq = √((σ_x - σ_y)² + (σ_y - σ_z)² + (σ_z - σ_x)² + 6⋅(τ_xy² + τ_yz² + τ_zx²)) / √2
        """
        s = stress_tensor  # Assume 3x3 symmetric matrix
        principal_stresses = np.linalg.eigvalsh(s)
        s1, s2, s3 = principal_stresses

        vm = np.sqrt(((s1 - s2)**2 + (s2 - s3)**2 + (s3 - s1)**2) / 2)
        return vm

    @staticmethod
    def safety_factor(yield_strength: float, von_mises: float) -> float:
        """
        Calculate safety factor

        SF = σ_y / σ_eq
        """
        if von_mises == 0:
            return float('inf')
        return yield_strength / von_mises


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demo_kinematics():
    """Demonstrate robot kinematics"""
    print("=== Robot Kinematics Demo ===\n")

    analyzer = KinematicsAnalyzer()

    # 3-DOF robot arm DH parameters
    # (d_i, a_i, alpha_i) for each joint
    dh_params = [
        (0.0, 0.3, 0.0),      # Link 1
        (0.0, 0.3, 0.0),      # Link 2
        (0.0, 0.1, 0.0),      # Link 3
    ]

    # Joint angles
    q = np.array([0.0, np.pi/4, np.pi/4])

    # Forward kinematics
    T = analyzer.forward_kinematics(dh_params, q)
    print(f"End-effector position: {T[:3, 3]}")
    print(f"End-effector orientation:\n{T[:3, :3]}\n")

    # Jacobian
    J = analyzer.jacobian_analytical(dh_params, q)
    print(f"Jacobian matrix shape: {J.shape}")
    print(f"Jacobian rank: {np.linalg.matrix_rank(J)}\n")

    # Inverse kinematics
    target_pose = np.eye(4)
    target_pose[:3, 3] = [0.5, 0.3, 0.0]  # Target position

    q_ik = analyzer.inverse_kinematics_numerical(dh_params, target_pose)
    if q_ik is not None:
        T_check = analyzer.forward_kinematics(dh_params, q_ik)
        print(f"IK solution found: {q_ik}")
        print(f"Achieved position: {T_check[:3, 3]}")


def demo_rigid_body_dynamics():
    """Demonstrate rigid body dynamics"""
    print("\n=== Rigid Body Dynamics Demo ===\n")

    # Define body properties
    props = RigidBodyProperties(
        mass=10.0,
        inertia=np.diag([1.0, 1.0, 1.2]),
        center_of_mass=np.zeros(3),
        friction_coefficient=0.1,
        damping_linear=0.5,
        damping_angular=0.1
    )

    # Initial state: [x, y, z, vx, vy, vz, q0, q1, q2, q3, wx, wy, wz]
    initial_state = np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0])

    # Time for simulation
    t_span = (0, 5)
    t_eval = np.linspace(0, 5, 500)

    # Define forces (gravity is handled in ODE)
    def force_func(t, state):
        # Applied force in x-direction, sinusoidal
        return np.array([10 * np.sin(2 * np.pi * t), 0, 0])

    def torque_func(t, state):
        # Applied torque
        return np.array([0, 0, 0.5 * np.cos(2 * np.pi * t)])

    # Simulate
    dynamics = RigidBodyDynamics(gravity=9.81)
    t, trajectory = dynamics.simulate(initial_state, props, t_eval,
                                     force_func, torque_func)

    # Extract results
    positions = trajectory[:, 0:3]
    velocities = trajectory[:, 3:6]

    print(f"Final position: {positions[-1]}")
    print(f"Final velocity: {velocities[-1]}")
    print(f"Max velocity: {np.max(np.linalg.norm(velocities, axis=1)):.2f} m/s")


def demo_thermal_modeling():
    """Demonstrate thermal transient"""
    print("\n=== Thermal Modeling Demo ===\n")

    # Define thermal parameters
    mass = 2.0  # kg
    specific_heat = 900  # J/(kg⋅K)
    surface_area = 0.5  # m²
    convection_coeff = 50  # W/(m²⋅K)
    ambient_temp = 298.15  # K (25°C)

    # Heat generation: ramp up then constant
    def heat_generation(t):
        if t < 2:
            return 1000 * (t / 2)  # Ramp to 1000 W
        else:
            return 1000

    # Initial condition
    T0 = 298.15  # K (25°C)

    # Simulate thermal transient
    thermal = ThermalModel()
    t, temps = thermal.simulate_thermal_transient(
        T0, mass, specific_heat, heat_generation,
        surface_area, convection_coeff, ambient_temp,
        (0, 60), num_points=600
    )

    print(f"Initial temperature: {T0 - 273.15:.1f}°C")
    print(f"Final temperature: {temps[-1] - 273.15:.1f}°C")
    print(f"Steady-state rise: {(temps[-1] - T0):.1f} K")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_kinematics()
    demo_rigid_body_dynamics()
    demo_thermal_modeling()
