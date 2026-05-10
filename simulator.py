import control
import numpy as np

def simulate_pid(num, den, Kp, Ki, Kd, t_end=10):
    plant = control.tf(num, den)
    pid = control.tf([Kd, Kp, Ki], [1, 0])
    closed_loop = control.feedback(pid * plant)

    t = np.linspace(0, t_end, 500)
    t_out, y_out = control.step_response(closed_loop, T=t)

    error = 1 - y_out
    u = np.zeros_like(error)
    dt = t_out[1] - t_out[0]
    integral = 0.0
    for i in range(1, len(error)):
        integral += error[i] * dt
        derivative = (error[i] - error[i-1]) / dt
        u[i] = Kp * error[i] + Ki * integral + Kd * derivative

    steady_state = float(y_out[-1])
    overshoot = (float(max(y_out)) - steady_state) / steady_state * 100 if steady_state != 0 else 0
    settling_idx = np.where(np.abs(y_out - steady_state) > 0.02 * abs(steady_state))[0]
    settling_time = float(t_out[settling_idx[-1]]) if len(settling_idx) > 0 else 0.0

    return t_out, y_out, u, {
        "overshoot": round(overshoot, 2),
        "settling_time": round(settling_time, 2),
        "steady_state": round(steady_state, 4),
        "u_max": round(float(max(abs(u))), 4),
        "u_final": round(float(u[-1]), 4)
    }

def pole_placement_pid(num, den, zeta=0.7, wn=2.0):
    sigma = zeta * wn
    p3 = 10 * sigma
    a2 = 2 * zeta * wn + p3
    a1 = wn**2 + 2 * zeta * wn * p3
    a0 = wn**2 * p3

    K = den[-1] if den[-1] != 0 else 1
    Kp = round(a1 / K, 3)
    Ki = round(a0 / K, 3)
    Kd = round((a2 - sum(den[:-1])) / K, 3)

    Kp = max(Kp, 0.1)
    Ki = max(Ki, 0.01)
    Kd = max(Kd, 0.0)

    return Kp, Ki, Kd