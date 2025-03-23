import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp

# -----------------------------
# 1. Define physical parameters
# -----------------------------
g = 30  # gravitational acceleration (m/s^2)
L1 = 1.0    # length of pendulum 1 (meters)
L2 = 1.0    # length of pendulum 2 (meters)
m1 = 1.0    # mass of bob 1 (kg)
m2 = 100.0    # mass of bob 2 (kg)

# Initial conditions: theta1, omega1, theta2, omega2

x1_0 = 0.0005 * (-201)
x2_0 = 0.0005 * 1

theta1_0 = np.arcsin(x1_0)
theta2_0 = np.arcsin(x2_0 - x1_0)

omega1_0 = 0.0
omega2_0 = 0.0

y0 = [theta1_0, omega1_0, theta2_0, omega2_0]

# Time span for the simulation
t_max = 1000  # seconds
t_eval = np.linspace(0, t_max, t_max * 50)


# ----------------------------------------
# 2. Define the ODE system (double pendulum)
# ----------------------------------------
def double_pendulum_ode(t, y, m1, m2, L1, L2, g):
    """
    y is [theta1, omega1, theta2, omega2]
    returns [dtheta1/dt, domega1/dt, dtheta2/dt, domega2/dt]
    """
    theta1, omega1, theta2, omega2 = y
    
    # Precompute repeated expressions
    sin1 = np.sin(theta1)
    sin2 = np.sin(theta2)
    cos1 = np.cos(theta1)
    cos2 = np.cos(theta2)
    sin12 = np.sin(theta1 - theta2)
    cos12 = np.cos(theta1 - theta2)

    denom = 2*m1 + m2 - m2 * np.cos(2*(theta1 - theta2))  # common denominator
    
    # dtheta1/dt = omega1
    dtheta1_dt = omega1
    
    # dtheta2/dt = omega2
    dtheta2_dt = omega2
    
    # domega1/dt
    num1 = -g*(2*m1 + m2)*sin1
    num2 = -m2*g*np.sin(theta1 - 2*theta2)
    num3 = -2*sin12*m2*(omega2**2*L2 + omega1**2*L1*cos12)
    domega1_dt = (num1 + num2 + num3) / (L1 * denom)
    
    # domega2/dt
    num4 = 2*sin12*(omega1**2*L1*(m1 + m2) + g*(m1 + m2)*cos1 + omega2**2*L2*m2*cos12)
    domega2_dt = num4 / (L2 * denom)

    return [dtheta1_dt, domega1_dt, dtheta2_dt, domega2_dt]


# ---------------------------------------
# 3. Solve the system using solve_ivp
# ---------------------------------------
solution = solve_ivp(
    fun=lambda t, y: double_pendulum_ode(t, y, m1, m2, L1, L2, g),
    t_span=(0, t_max),
    y0=y0,
    t_eval=t_eval,
    vectorized=False
)

theta1_sol = solution.y[0]
omega1_sol = solution.y[1]
theta2_sol = solution.y[2]
omega2_sol = solution.y[3]
time = solution.t

# -----------------------------------------
# 4. Prepare coordinates for the animation
# -----------------------------------------
# Pendulum 1 position (x1, y1)
x1 = L1 * np.sin(theta1_sol)
y1 = -L1 * np.cos(theta1_sol)

# Pendulum 2 position (x2, y2), relative to the pivot of the second rod
x2 = x1 + L2 * np.sin(theta2_sol)
y2 = y1 - L2 * np.cos(theta2_sol)

# ------------------------------------------------
# 5. Set up the figure and animation function
# ------------------------------------------------
fig, ax = plt.subplots(figsize=(5,5))
ax.set_xlim(0.5*(-L1 - L2 - 0.2), 0.5*(L1 + L2 + 0.2))
ax.set_ylim(-L1 - L2 - 0.2, 0)
ax.set_aspect(2, adjustable = 'box')
ax.set_title('Double Pendulum Simulation')

line, = ax.plot([], [], 'o-', lw=2)

def init():
    line.set_data([], [])
    return line,

def update(i):
    # Points for the first pivot (the origin, at (0,0)), 
    # the first mass (x1[i], y1[i]), and the second mass (x2[i], y2[i])
    this_x = [0, x1[i], x2[i]]
    this_y = [0, y1[i], y2[i]]
    
    line.set_data(this_x, this_y)
    return line,

anim = FuncAnimation(fig, update, frames=len(time), init_func=init, interval=50, blit=True)

plt.show()
