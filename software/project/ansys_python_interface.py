# python & ansoft connection

from win32com import client
import pythoncom
import os


def restore_project(ctx):
    project_name = ctx["data"]["project_name"]
    project_path = ctx["data"]["project_path"]

    print(ctx["data"]["spec_params"])

    pythoncom.CoInitialize()
    oAnsoftApp = client.Dispatch("Ansoft.ElectronicsDesktop")

    oDesktop = oAnsoftApp.GetAppDesktop()
    oProject = oDesktop.OpenProject(project_path + "\\" + project_name + ".aedt")
    oDesign = oProject.GetActiveDesign()
    oEditor = oDesign.SetActiveEditor("3D Modeler")

    ctx["ansys_object"]["oProject"] = oProject
    ctx["ansys_object"]["oDesign"] = oDesign
    ctx["ansys_object"]["oEditor"] = oEditor
    ctx["ansys_object"]["oDesktop"] = oDesktop

    return ctx

def close_project(ctx):
    project_name = ctx["data"]["project_name"]

    ctx["ansys_object"]["oDesktop"].CloseProject(project_name)

    return ctx

def clear_data(ctx):
    ctx["ansys_object"]["oDesign"].DeleteFullVariation("All", False)

    return ctx

def save_project(ctx):
    project_name = ctx["data"]["project_name"]
    project_path = ctx["data"]["project_path"]

    if not os.path.isdir(project_path):
        os.mkdir(project_path)

    ctx["ansys_object"]["oProject"].SaveAs(project_path + "\\" + project_name + ".aedt", True)

    return ctx
