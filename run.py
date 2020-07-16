import os
import datetime
import time

# project
from software.project.ansys_python_interface import restore_project, close_project, save_project

# setting
from software.setting.optimetrics_setting import optimetrics_setting, delete_opt_setting
from software.setting.analysis_setting import start_analysis
from software.setting.report_setting import create_and_export_report
from software.setting.export_plot_setting import export_model_picture

# postprocess
from postprocess.result import result_process

# debug
# import ipdb; ipdb.set_trace()
# from win32com import client
# oAnsoftApp = client.Dispatch("Ansoft.ElectronicsDesktop")
# oDesktop = oAnsoftApp.GetAppDesktop()
# oProject = oDesktop.SetActiveProject("project_1592523833")
# oDesign = oProject.SetActiveDesign("Maxwell2DDesign1")
# oEditor = oDesign.SetActiveEditor("3D Modeler")

# other
# from params.geometry_params_checking import geometry_params_checking
# geomotry_errors = geometry_params_checking({**stator_params, **rotor_params})

# if geomotry_errors['error_present?']:
#     raise BaseException(geomotry_errors['error_msg'])

spec_params = {
    "ai_response":{
        "wmw":         11,
        "wmt":         2.5,
        "am":          85,
        "delta":       40,
        "R1":          0,
    },
    "export_path": None,
    "pj_key":      str(int(time.mktime(datetime.datetime.now().timetuple()))),
    "res_url":     None,
}


def run_ansys(ctx):
    spec = {**spec_params, **ctx["request"]}

    time_stamp = str(spec["pj_key"])
    data_folder = str(datetime.date.today()).replace("-", "_") + "_" + time_stamp
    project_path = os.path.join(os.getcwd(), "software", "project")

    ctx = {
        **ctx,
        "ansys_object": {
            "oProject": None,
            "oDesign": None,
            "oEditor": None,
            "oDesktop": None,
        },
        "data": {
            "spec_params": spec,
            "data_folder": data_folder,
            "project_name": "3_7kw_max",
            "project_path": project_path,
            "coil_name_list": [],
            "mag_name_list": [],
            "opt_name": "OPT",
            "opt_oModule": None,
            "report_moudule": None,
            "time_stamp": time_stamp,
            "export_path": spec["export_path"] or os.path.join(os.getcwd(), "tmp", data_folder),
            "model_picture_path": None,
        },
        "response": {
            "pj_key": spec["pj_key"],
            "stator_OD": 125,
            "motor_length": 150,
            "coil_turn": 3,
            "ele_ang_x_axis": [],
            "corner_point": {
                "current": 80,
                "speed": 3000,
                "torque_data": [],
                "avg_torque": None,
                "torque_ripple": None,
                "line_voltage_rms": None,
                "core_loss": None,
                "core_loss_factor": None,
                "copper_loss": None,
                "efficiency": None,
                "output_power": None,
                "current_density": None,
            },
            "noload": {
                "ph_voltage_data": [],
                "cogging_data": [],
                "ph_voltage_rms": None,
                "cogging": None,
                "speed": 1000,
            },
            "max_speed": {
                "line_voltage_rms": None,
                "speed": None,
            },
            "material_name": {
                "stator": None,
                "rotor": None,
                "magnet": None
            }
        }
    }

    restore_project(ctx) and \
        export_model_picture(ctx) and \
        optimetrics_setting(ctx) and \
        start_analysis(ctx) and \
        create_and_export_report(ctx) and \
        save_project(ctx) and \
        close_project(ctx) and \
        result_process(ctx)

    print(ctx["response"])
    print('Simulation Completed')

    # ctx["response"] = ctx["params"]["motor_cal_params"]

    return ctx


if __name__ == "__main__":
    run_ansys({"request": {"call": "just for test"}})
