import pandas as pd
import numpy as np
import math
import os


def np_rms(arr):
    return np.sqrt((arr ** 2).sum() / arr.size)

def result_process(ctx):
    response = ctx["response"]
    result_ctx = {
        "data_path": ctx["data"]["export_path"],
        "data": {
            "copper":{
                "temp": 30,
                "slot_distance": 14.6,
                "coil_cross_slot_num": 1,
                "motor_length": response["motor_length"],
                "coil_turn": response["coil_turn"],
                "para_conductor": 17,
                "conductor_OD": 1,
                "y_para": 1,
                "copper_ele_resistivity": 1/58,
                "correct_ratio": 1.2,
            },
        },
        "result": {
            "model_picture_path": ctx["data"]["model_picture_path"],
            "corner_point": {
                "current": 80,
                "speed": 3000,
                "avg_torque": None,
                "torque_ripple": None,
                "line_voltage_rms": None,
                "core_loss": None,
                "core_loss_factor": 1,
                "copper_loss": None,
                "efficiency": None,
                "output_power": None,
                "current_density": 18,
            },
        }
    }

    process_toruqe(result_ctx) and \
        process_voltage(result_ctx) and \
        process_core_loss(result_ctx) and \
        process_copper_loss(result_ctx) and \
        process_efficiency(result_ctx)

    ctx["response"] = {**ctx["response"], **result_ctx["result"]}

    return ctx


def process_toruqe(result_ctx):
    tq_df = pd.read_csv(os.path.join(result_ctx["data_path"], "torque.csv"))
    corner_current = result_ctx["result"]["corner_point"]["current"]

    torque_data_arr = tq_df.filter(like=str(corner_current) + "A").dropna().values.flatten()

    result_ctx["result"]["corner_point"]["avg_torque"] = torque_data_arr.mean()
    result_ctx["result"]["corner_point"]["torque_ripple"] = (
        torque_data_arr.max() - torque_data_arr.min()) / torque_data_arr.mean() * 100

    return result_ctx


def process_voltage(result_ctx):
    corner_current = result_ctx["result"]["corner_point"]["current"]

    vol_line = pd.read_csv(os.path.join(result_ctx["data_path"], "voltage_line.csv"))
    cor_vol_data_arr = vol_line.filter(like=str(corner_current) + "A").dropna().values.flatten()

    result_ctx["result"]["corner_point"]["line_voltage_rms"] = np_rms(cor_vol_data_arr)

    return result_ctx

def process_core_loss(result_ctx):
    core_loss = pd.read_csv(os.path.join(result_ctx["data_path"], "coreloss.csv"))
    corner_current = result_ctx["result"]["corner_point"]["current"]

    cor_core_loss_data_arr = core_loss.filter(like=str(corner_current) + "A").dropna().values.flatten()

    result_ctx["result"]["corner_point"]["core_loss"] = cor_core_loss_data_arr[-5:].mean()

    return result_ctx

def process_copper_loss(result_ctx):
    corner_current = result_ctx["result"]["corner_point"]["current"]
    copper_data    = result_ctx["data"]["copper"]

    slot_distance          = copper_data["slot_distance"]
    coil_cross_slot_num    = copper_data["coil_cross_slot_num"]
    coil_turn              = copper_data["coil_turn"]
    para_conductor         = copper_data["para_conductor"]
    conductor_OD           = copper_data["conductor_OD"]
    copper_ele_resistivity = copper_data["copper_ele_resistivity"]
    motor_length           = copper_data["motor_length"]
    temp                   = copper_data["temp"]
    correct_ratio          = copper_data["correct_ratio"]
    y_para                 = copper_data["y_para"]

    single_coil_dist = slot_distance * coil_cross_slot_num * math.pi + motor_length * 2
    single_coil_resis = copper_ele_resistivity * (1 / (conductor_OD**2 * math.pi/4 * 1000)) * single_coil_dist * coil_turn / para_conductor
    total_coil_resis = single_coil_resis * correct_ratio / y_para
    resis_with_temp = total_coil_resis * (1 + 0.004 * (temp - 20))

    result_ctx["result"]["corner_point"]["copper_loss"] = 3 * corner_current ** 2 * resis_with_temp

    return result_ctx


def process_efficiency(result_ctx):
    corner_point = result_ctx["result"]["corner_point"]
    torque = corner_point["avg_torque"]
    speed = corner_point["speed"]
    core_loss = corner_point["core_loss"] * corner_point["core_loss_factor"]
    copper_loss = corner_point["copper_loss"]

    output_power = torque * speed * 2 * math.pi / 60
    efficiency = output_power / (output_power + core_loss + copper_loss)

    result_ctx["result"]["corner_point"]["output_power"] = output_power
    result_ctx["result"]["corner_point"]["efficiency"] = round(efficiency * 100, 2)

    return result_ctx

# import ipdb; ipdb.set_trace()
# result_ctx = {
#     "data_path": os.path.join(os.getcwd(), "tmp", "2020_07_10_1594386431"),
#     "total_step": 50,
#     "data": {
#         "copper":{
#             "temp": 30,
#             "slot_distance": 14.6,
#             "coil_cross_slot_num": 1,
#             "motor_length": 150,
#             "coil_turn": 3,
#             "para_conductor": 17,
#             "conductor_OD": 1,
#             "y_para": 1,
#             "copper_ele_resistivity": 1/58,
#             "correct_ratio": 1.2,
#         },
#     },
#     "result": {
#         "model_picture_path": None,
#         "ele_ang_x_axis": [],
#         "stator_OD": 110,
#         "motor_length": 50,
#         "coil_turn": 2,
#         "corner_point": {
#             "current": 80,
#             "speed": 3000,
#             "torque_data": [],
#             "avg_torque": None,
#             "torque_ripple": None,
#             "line_voltage_rms": None,
#             "core_loss": None,
#             "core_loss_factor": 1,
#             "copper_loss": None,
#             "efficiency": None,
#             "output_power": None,
#             "current_density": None,
#         },
#     }
# }

# process_toruqe(result_ctx) and \
#     process_voltage(result_ctx) and \
#     process_core_loss(result_ctx) and \
#     process_copper_loss(result_ctx) and \
#     process_efficiency(result_ctx)
# print(result_ctx)
