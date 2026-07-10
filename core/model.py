import numpy as np

def initialize_parameters(d, h):
    scale_in = np.sqrt(2.0 / (d + h))
    scale_rec = np.sqrt(2.0 / (h + h))
    
    return {
        "W_z": np.random.randn(h, d) * scale_in,
        "U_z": np.random.randn(h, h) * scale_rec,
        "b_z": np.zeros((h, 1)),
        
        "W_r": np.random.randn(h, d) * scale_in,
        "U_r": np.random.randn(h, h) * scale_rec,
        "b_r": np.zeros((h, 1)),
        
        "W_h": np.random.randn(h, d) * scale_in,
        "U_h": np.random.randn(h, h) * scale_rec,
        "b_h": np.zeros((h, 1)),
        
        "W_y": np.random.randn(1, h) * np.sqrt(2.0 / h),
        "b_y": np.zeros((1, 1))
    }

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def gru_single_step(x_t, h_prev, params):
    W_z, U_z, b_z = params["W_z"], params["U_z"], params["b_z"]
    W_r, U_r, b_r = params["W_r"], params["U_r"], params["b_r"]
    W_h, U_h, b_h = params["W_h"], params["U_h"], params["b_h"]
    
    z_t = sigmoid(np.dot(W_z, x_t) + np.dot(U_z, h_prev) + b_z)
    r_t = sigmoid(np.dot(W_r, x_t) + np.dot(U_r, h_prev) + b_r)
    tilde_h_t = np.tanh(np.dot(W_h, x_t) + np.dot(U_h, (r_t * h_prev)) + b_h)
    h_t = (1 - z_t) * h_prev + z_t * tilde_h_t
    
    return h_t, z_t, r_t, tilde_h_t

def gru_forward_sequence(X_seq, params):
    T, d = X_seq.shape
    h = params["b_z"].shape[0]
    h_t = np.zeros((h, 1))
    step_history = []
    
    for t in range(T):
        x_t = X_seq[t].reshape(d, 1)
        h_t, z_t, r_t, tilde_h_t = gru_single_step(x_t, h_t, params)
        step_history.append((h_t, z_t, r_t, tilde_h_t, x_t))
        
    y_pred = sigmoid(np.dot(params["W_y"], h_t) + params["b_y"])
    return y_pred, h_t, step_history

def gru_backward_sequence(y_true, y_pred, step_history, params):
    h, d = params["W_z"].shape
    T = len(step_history)
    grads = {k: np.zeros_like(v) for k, v in params.items()}
    
    dy = y_pred - y_true
    h_T = step_history[-1][0]
    grads["W_y"] = np.dot(dy, h_T.T)
    grads["b_y"] = dy
    
    dh_next = np.dot(params["W_y"].T, dy)
    
    for t in reversed(range(T)):
        h_t, z_t, r_t, tilde_h_t, x_t = step_history[t]
        h_prev = step_history[t-1][0] if t > 0 else np.zeros((h, 1))
        
        datilde_h = dh_next * z_t * (1 - tilde_h_t ** 2)
        daz = dh_next * (tilde_h_t - h_prev) * z_t * (1 - z_t)
        dh_prev_reset = np.dot(params["U_h"].T, datilde_h)
        dar = (dh_prev_reset * h_prev) * r_t * (1 - r_t)
        
        grads["W_h"] += np.dot(datilde_h, x_t.T)
        grads["U_h"] += np.dot(datilde_h, (r_t * h_prev).T)
        grads["b_h"] += datilde_h
        
        grads["W_z"] += np.dot(daz, x_t.T)
        grads["U_z"] += np.dot(daz, h_prev.T)
        grads["b_z"] += daz
        
        grads["W_r"] += np.dot(dar, x_t.T)
        grads["U_r"] += np.dot(dar, h_prev.T)
        grads["b_r"] += dar
        
        dh_next = (dh_next * (1 - z_t) + dh_prev_reset * r_t + 
                   np.dot(params["U_z"].T, daz) + np.dot(params["U_r"].T, dar))
        
    return grads

def update_parameters(params, grads, lr):
    for k in params.keys():
        params[k] -= lr * np.clip(grads[k], -5.0, 5.0)
    return params