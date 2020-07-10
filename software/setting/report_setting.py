import os

def create_and_export_report(ctx):
    report_list = {
        "torque": ["Moving1.Torque", "Time"],
        "voltage_line": ["InducedVoltage(PhaseA)-InducedVoltage(PhaseB)", "Time"],
        "coreloss": ["CoreLoss", "Time"],
    }

    report_ctx = {
        "moudule": ctx["ansys_object"]["oDesign"].GetModule("ReportSetup"),
        "report_name": "data_table",
        "report_list": report_list,
        "export_path": ctx["data"]["export_path"],
    }

    create_reports(report_ctx) and \
        export_reports(report_ctx) and \
        remove_all_report(report_ctx)

    return ctx

def create_reports(report_ctx):
    for data_name, x_axis in report_ctx["report_list"].values():
        report_ctx["moudule"].CreateReport(data_name, "Transient", "Rectangular Plot", "Setup1 : Transient",
                [
                        "Domain:="		, "Sweep"
                ],
                [
                        "Time:="		, ["All"],
                        "Irms:="		, ["All"],
                        "wtb:="		, ["All"],
                        "d3:="		, ["All"],
                        "d2:="		, ["All"],
                        "d1:="		, ["All"],
                        "ws:="		, ["All"],
                        "R1:="		, ["All"],
                        "airgap:="		, ["All"],
                        "rotorio:="		, ["All"],
                        "wmw:="		, ["All"],
                        "wmt:="		, ["All"],
                        "am:="		, ["All"],
                        "mx:="		, ["All"],
                        "ml:="		, ["All"],
                        "rib:="		, ["All"],
                        "thickness:="	, ["All"],
                        "Sp:="		, ["All"],
                        "turns:="		, ["All"],
                        "delta:="		, ["All"],
                        "Id:="		, ["All"],
                        "Iq:="		, ["All"],
                        "wbi:="		, ["All"]
                ],
                [
                        "X Component:="		, x_axis,
                        "Y Component:="		, [data_name]
                ], [])

    return report_ctx


def export_reports(report_ctx):
    export_path = report_ctx["export_path"]

    for report_name, data_with_x_axis in report_ctx["report_list"].items():
        data_name, _ = data_with_x_axis

        report_ctx["moudule"].ExportToFile(
            data_name, export_path + "\\" + report_name + ".csv")

    return report_ctx

def remove_all_report(report_ctx):
    print("remove all report")
    report_ctx["moudule"].DeleteAllReports()

    return report_ctx
