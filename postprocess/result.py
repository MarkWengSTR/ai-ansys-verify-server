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
    noload_speed = result_ctx["result"]["noload"]["speed"]
    corner_current = result_ctx["result"]["corner_point"]["current"]
    corner_speed = result_ctx["result"]["corner_point"]["speed"]

    cogging_data_arr = tq_df.filter(like="0A").filter(
        like=str(noload_speed) + "rpm").dropna().values.flatten()
    torque_data_arr = tq_df.filter(like=str(corner_current) + "A").filter(
        like=str(corner_speed) + "rpm").dropna().values.flatten()

    # result_ctx["result"]["noload"]["cogging_data"] = cogging_data_arr.tolist()
    # result_ctx["result"]["noload"]["cogging"] = cogging_data_arr.max() - \
    #     cogging_data_arr.min()

    # result_ctx["result"]["corner_point"]["torque_data"] = torque_data_arr.tolist()
    result_ctx["result"]["corner_point"]["avg_torque"] = torque_data_arr.mean()
    result_ctx["result"]["corner_point"]["torque_ripple"] = (
        torque_data_arr.max() - torque_data_arr.min()) / torque_data_arr.mean() * 100

    return result_ctx


def process_voltage(result_ctx):
    vol_ph = pd.read_csv(os.path.join(result_ctx["data_path"], "voltage_ph.csv"))
    vol_line = pd.read_csv(os.path.join(result_ctx["data_path"], "voltage_line.csv"))
    # noload_speed   = result_ctx["result"]["noload"]["speed"]
    # corner_current = result_ctx["result"]["corner_point"]["current"]
    # corner_speed   = result_ctx["result"]["corner_point"]["speed"]
    # max_speed      = result_ctx["result"]["max_speed"]["speed"]

    bemf_ph_data_arr = vol_ph.filter(like="0A").filter(
        like=str(noload_speed) + "rpm").dropna().values.flatten()
    bemf_line_data_arr = vol_line.filter(like="0A").filter(
        like=str(noload_speed) + "rpm").dropna().values.flatten()
    cor_vol_data_arr = vol_line.filter(like=str(corner_current) + "A").filter(
        like=str(corner_speed) + "rpm").dropna().values.flatten()

    # result_ctx["result"]["noload"]["ph_voltage_data"] = bemf_ph_data_arr.tolist()
    # result_ctx["result"]["noload"]["ph_voltage_rms"] = np_rms(bemf_ph_data_arr)
    # result_ctx["result"]["max_speed"]["line_voltage_rms"] = np_rms(bemf_line_data_arr) * (max_speed / noload_speed)
    result_ctx["result"]["corner_point"]["line_voltage_rms"] = np_rms(cor_vol_data_arr)

    return result_ctx

def process_core_loss(result_ctx):
    core_loss = pd.read_csv(os.path.join(result_ctx["data_path"], "coreloss.csv"))
    corner_current = result_ctx["result"]["corner_point"]["current"]
    corner_speed = result_ctx["result"]["corner_point"]["speed"]

    cor_core_loss_data_arr = core_loss.filter(like=str(corner_current) + "A").filter(
        like=str(corner_speed) + "rpm").dropna().values.flatten()

    result_ctx["result"]["corner_point"]["core_loss"] = cor_core_loss_data_arr[-5:].mean()

    return result_ctx

def process_copper_loss(result_ctx):
    corner_current = result_ctx["result"]["corner_point"]["current"]
    copper_data    = result_ctx["data"]["copper"]

    slot_distance          = copper_data["slot_distance"]
    coil_cross_slot_num    = copper_data["coil_cross_slot_num"]
    coil_turns             = copper_data["coil_turns"]
    para_conductor         = copper_data["para_conductor"]
    conductor_OD           = copper_data["conductor_OD"]
    copper_ele_resistivity = copper_data["copper_ele_resistivity"]
    motor_length           = copper_data["motor_length"]
    temp                   = copper_data["temp"]
    correct_ratio          = copper_data["correct_ratio"]
    y_para                 = copper_data["y_para"]

    single_coil_dist = slot_distance * coil_cross_slot_num * math.pi + motor_length * 2
    single_coil_resis = copper_ele_resistivity * (1 / (conductor_OD**2 * math.pi/4 * 1000)) * single_coil_dist * coil_turns / para_conductor
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
#     "data_path": os.path.join(os.getcwd(), "tmp", "2020_06_21_1592743691"),
#     "total_step": 50,
#     "data": {
#         "copper": {
#             "temp": 30,
#             "slot_distance": 21.2319,
#             "coil_cross_slot_num": 1,
#             "motor_length": 96,
#             "coil_turns": 2,
#             "para_conductor": 18,
#             "conductor_OD": 1,
#             "y_para": 1,
#             "copper_ele_resistivity": 1/58,
#             "correct_ratio": 1.2,
#         },
#     },
#     "result": {
#         "model_picture_path": None,
#         "ele_ang_x_axis": [],
        # "stator_OD": 110,
        # "motor_length": 50,
        # "coil_turn": 2,
#         "corner_point": {
#             "current": 297,
#             "speed": 1769,
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
#         "noload": {
#             "ph_voltage_data": [],
#             "cogging_data": [],
#             "ph_voltage_rms": None,
#             "cogging": None,
#             "speed": 1000,
#         },
#         "max_speed": {
#             "line_voltage_rms": None,
#             "speed": 5000,
#         },
#         "material_name": {
#             "stator": None,
#             "rotor": None,
#             "magnet": None
#         }
#     }
# }

# prepare_x_axis_ele_ang(result_ctx) and \
#     process_toruqe(result_ctx) and \
#     process_voltage(result_ctx) and \
#     process_core_loss(result_ctx) and \
#     process_copper_loss(result_ctx) and \
#     process_efficiency(result_ctx)
