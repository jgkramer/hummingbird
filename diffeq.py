import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Define the system with y'' = -y * |y|
def system1(t, y):
    y1, y2 = y
    dy1_dt = y2
    dy2_dt = -(y1 ** 3)
    return [dy1_dt, dy2_dt]


def system2(t, y):
    y1, y2 = y
    dy1_dt = y2
    dy2_dt = -y1
    return [dy1_dt, dy2_dt]

# Initial conditions: y(0) = 1, y'(0) = 0
y0 = [0.1, 0.0]

# Time domain
t_span = (0, 100)
t_eval = np.linspace(*t_span, 1000)

# Solve the system
sol1 = solve_ivp(system1, t_span, y0, t_eval=t_eval, method='RK45')
sol2 = solve_ivp(system2, t_span, y0, t_eval=t_eval, method='RK45')

# Plot the result
plt.plot(sol1.t, sol1.y[0], label='y'' = -y^3')
plt.plot(sol2.t, sol2.y[0], label='y'' = -y')

plt.xlabel('t')
plt.ylabel('y')

plt.legend()
plt.grid(True)
plt.show()
