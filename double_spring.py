import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp


# -----------------------------
# 1. Define physical parameters
# -----------------------------

k1 = 20.0
k2 = 20.0
L1 = 1.0    # length of pendulum 1 (meters)
L2 = 1.0    # length of pendulum 2 (meters)
m1 = 1.0    # mass of bob 1 (kg)
m2 = 1.0    # mass of bob 2 (kg)

framespeed = 40

# Initial conditions: theta1, omega1, theta2, omega2

scale = 0.25
y1_0 = 0.5*(-np.sqrt(5)-1)*scale
y2_0 = 1*scale

v1_0 = 0
v2_0 = 0

y0 = [y1_0, v1_0, y2_0, v2_0]

# Time span for the simulation
t_max = 1000  # seconds
t_eval = np.linspace(0, t_max, t_max * framespeed)

def h1(t):
    return 0

# ----------------------------------------
# 2. Define the ODE system (double pendulum)
# ----------------------------------------
def double_spring_ode(t, y, m1, m2):
    """
    y is [y1, v1, y2, v3]
    returns [dy1/dt, dv1/dt, dy2/dt, dv2/dt]
    """
    y1, v1, y2, v2 = y
    
    
    # dy/dt = v
    dy1_dt = v1
    dy2_dt = v2
    
    # a1
    F1_net = k1*(h1(t)-y1)-k2*(y1-y2)
    a1 = F1_net/m1
     
    # a2
    F2_net = k2*(y1-y2)
    a2 = F2_net/m2

    return [v1, a1, v2, a2]

# ---------------------------------------
# 3. Solve the system using solve_ivp
# ---------------------------------------
solution = solve_ivp(
    fun=lambda t, y: double_spring_ode(t, y, m1, m2),
    t_span=(0, t_max),
    y0=y0,
    t_eval=t_eval,
    vectorized=False
)

y1_sol = solution.y[0]
v1_sol = solution.y[1]
y2_sol = solution.y[2]
v2_sol = solution.y[3]
time = solution.t

# -----------------------------------------
# 4. Prepare coordinates for the animation
# -----------------------------------------
# Pendulum 1 position (x1, y1)

y1 = 0-L1-y1_sol
x1 = [0]*len(y1_sol)

# Pendulum 2 position (x2, y2), relative to the pivot of the second rod

y2 = 0-L1-L2-y2_sol
x2 = [0]*len(y2_sol)

# ------------------------------------------------
# 5. Set up the figure and animation function
# ------------------------------------------------
fig, ax = plt.subplots(figsize=(5,5))
ax.set_xlim(-1, 1)
ax.set_ylim(-1.5*(L1+L2), 0)
ax.set_aspect(2, adjustable = 'box')
ax.set_title('Double Spring Simulation')

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

anim = FuncAnimation(fig, update, frames=len(time), init_func=init, interval=framespeed, blit=True)

plt.show()
