"""Translate .vspcript"""
import openvsp as vsp

fname = "VSPAEROtests.vsp3"

# %% Define functions


def GenerateGeom():

    # ==== Create some test geometries ====
    print("--> Generating Geometries")
    print("")

    pod_id = vsp.AddGeom("POD", "")
    wing_id = vsp.AddGeom("WING", "")

    vsp.SetParmVal(wing_id, "X_Rel_Location", "XForm", 2.5)
    vsp.SetParmVal(wing_id, "TotalArea", "WingGeom", 25)

    subsurf_id = vsp.AddSubSurf(wing_id, vsp.SS_CONTROL, 0)

    vsp.Update()

    # ==== Setup export filenames ====
    fname_vspaerotests = fname

    # ==== Save Vehicle to File ====
    print("-->Saving vehicle file to: ")
    print(fname_vspaerotests)
    print("")
    vsp.WriteVSPFile(fname)
    print("COMPLETE\n")
    vsp.Update()


def TestVSPAeroComputeGeom():
    print("-> Begin TestVSPAeroComputeGeom")
    print("")

    # open the file created in GenerateGeom
    fname_vspaerotests = fname
    vsp.ReadVSPFile(fname_vspaerotests)  # Sets VSP3 file name

    # ==== Analysis: VSPAero Compute Geometry ====
    analysis_name = "VSPAEROComputeGeometry"
    print(analysis_name)

    # Set defaults
    vsp.SetAnalysisInputDefaults(analysis_name)

    # Analysis method
    analysis_method = list(vsp.GetIntAnalysisInput(
        analysis_name, "AnalysisMethod"))
    analysis_method[0] = vsp.VORTEX_LATTICE
    vsp.SetIntAnalysisInput(analysis_name, "AnalysisMethod", analysis_method)

    # list inputs, type, and current values
    vsp.PrintAnalysisInputs(analysis_name)
    print("")

    # Execute
    print("\tExecuting...")
    rid = vsp.ExecAnalysis(analysis_name)
    print("COMPLETE")

    # Get & Display Results
    vsp.PrintResults(rid)

# %%


def TestVSPAeroComputeGeomPanel():
    print("-> Begin TestVSPAeroComputeGeomPanel")
    print("")

    # open the file created in GenerateGeom
    fname_vspaerotests = fname
    vsp.ReadVSPFile(fname_vspaerotests)  # Sets VSP3 file name

    # ==== Analysis: VSPAero Compute Geometry ====#
    analysis_name = "VSPAEROComputeGeometry"
    print(analysis_name)

    # Set defaults
    vsp.SetAnalysisInputDefaults(analysis_name)

    # Set to panel method
    analysis_method = list(vsp.GetIntAnalysisInput(
        analysis_name, "AnalysisMethod"))
    analysis_method[0] = vsp.PANEL
    vsp.SetIntAnalysisInput(analysis_name, "AnalysisMethod", analysis_method)

    # list inputs, type, and current values
    vsp.PrintAnalysisInputs(analysis_name)
    print("")

    # Execute
    print("\tExecuting...")
    rid = vsp.ExecAnalysis(analysis_name)
    print("COMPLETE")

    # Get & Display Results
    vsp.PrintResults(rid)


# %% Sharp TE function

# def TestVSPAeroSharpTrailingEdge():

#    print("-> Begin TestVSPAeroSharpTrailingEdge\n")

#    # ==== Analysis: VSPAero Single Point ====
#    analysis_name = "VSPAEROSinglePoint"
#    print(analysis_name)

#    # ==== Create some test geometries ====
#    print("--> Generating Geometries\n")

#    wing_id = vsp.AddGeom("WING", "")

#    # Get Section IDs
#    wingxsurf_id = vsp.GetXSecSurf(wing_id, 0)
#    # xsec_id0 = vsp.GetXSec(wingxsurf_id, 0)
#    xsec_id1 = vsp.GetXSec(wingxsurf_id, 1)

#    # Set Root and Tip Chord to 3:
#    vsp.SetDriverGroup(wing_id, 1, vsp.AREA_WSECT_DRIVER,
#                       vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
#    vsp.SetParmVal(wing_id, "Root_Chord", "XSec_1", 3.0)
#    vsp.SetParmVal(wing_id, "Tip_Chord", "XSec_1", 3.0)
#    vsp.SetParmVal(wing_id, "Area", "XSec_1", 25.0)

#    # Set Sweep to 0:
#    xsweep_id1 = vsp.GetXSecParm(xsec_id1, "Sweep")
#    vsp.SetParmVal(xsweep_id1, 0.0)

#    # Increase W Tesselation:
#    vsp.SetParmVal(wing_id, "Tess_W", "Shape", 69)

#    # Increase U Tesselation
#    xutess_id1 = vsp.GetXSecParm(xsec_id1, "SectTess_U")
#    vsp.SetParmVal(xutess_id1, 16)

#    vsp.Update()

#    # ==== Save Vehicle to File ====
#    print("-->Saving VSP model\n")
#    fname = "TestVSPAeroSharpTrailingEdge.vsp3"
#    vsp.WriteVSPFile(fname, vsp.SET_ALL)
#    vsp.Update()

#    # Close and open the file
#    #vsp.ClearVSPModel()
#    #vsp.Update()
#    vsp.ReadVSPFile(fname)   # Sets VSP3 file name
#    vsp.Update()

#    # ==== Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File ====
#    compgeom_name = "VSPAEROComputeGeometry"
#    print(compgeom_name)

#    # Set defaults
#    vsp.SetAnalysisInputDefaults(compgeom_name)

#    # analysis_method = list(vsp.GetIntAnalysisInput(
#    #    compgeom_name, "AnalysisMethod"))
#    # analysis_method[0] = vsp.VORTEX_LATTICE
#    # vsp.SetIntAnalysisInput(compgeom_name, "AnalysisMethod", analysis_method)

#    # list inputs, type, and current values
#    vsp.PrintAnalysisInputs(compgeom_name)

#    # Execute
#    print("\tExecuting...")
#    compgeom_resid = vsp.ExecAnalysis(compgeom_name)
#    print("COMPLETE")

#    # Get & Display Results
#    vsp.PrintResults(compgeom_resid)

#    # ==== Analysis: VSPAero Single Point ====
#    # Set defaults
#    vsp.SetAnalysisInputDefaults(analysis_name)

#    # Reference geometry set
#    geom_set = []
#    geom_set.append(0)
#    vsp.SetIntAnalysisInput(analysis_name, "GeomSet", geom_set, 0)
#    ref_flag = []
#    ref_flag.append(1)
#    vsp.SetIntAnalysisInput(analysis_name, "RefFlag", ref_flag, 0)
#    wid = vsp.FindGeomsWithName("WingGeom")
#    vsp.SetStringAnalysisInput(analysis_name, "WingID", wid, 0)

#    # Freestream Parameters
#    alpha = []
#    alpha.append(0.0)
#    vsp.SetDoubleAnalysisInput(analysis_name, "Alpha", alpha, 0)
#    mach = []
#    mach.append(0.1)
#    vsp.SetDoubleAnalysisInput(analysis_name, "Mach", mach, 0)

#    vsp.Update()

#    # list inputs, type, and current values
#    vsp.PrintAnalysisInputs(analysis_name)
#    print("")

#    # Execute
#    print("\tExecuting...")
#    rid = vsp.ExecAnalysis(analysis_name)
#    print("COMPLETE")

#    # Get & Display Results
#    vsp.PrintResults(rid)

#    history_res = vsp.FindLatestResultsID("VSPAERO_History")
#    load_res = vsp.FindLatestResultsID("VSPAERO_Load")

#    CL = vsp.GetDoubleResults(history_res, "CL", 0)
#    cl = vsp.GetDoubleResults(load_res, "cl", 0)

#    # print("CL at 0 angle of attack: ", false)

#    # for (int i = 0 i < int(CL.size()) i ++ )
#    # {
#    #    print(CL[i], false)
#    # }
#    # print("")

#    # print("cl at 0 angle of attack: ", false)
#    # for (int j = 0 j < int(cl.size()) j ++ )
#    # {
#    #    print(cl[j], false)
#    # }
#    # print("")
    # print("")

# %% TestAll function


def TestAll():
    # vsp.ClearVSPModel()
    # ==== Generate Geometry ====#
    GenerateGeom()
    # vsp.ClearVSPModel()

    # # ==== Vortex Lattice Method ====#
    # TestVSPAeroComputeGeom()
    # # vsp.ClearVSPModel()

    # # # ==== Panel Method ====#
    # # TestVSPAeroComputeGeomPanel()
    # # vsp.ClearVSPModel()

    # # ==== Sharp Trailing Edge Test ====//
    # #TestVSPAeroSharpTrailingEdge()

    # vsp.ClearVSPModel()

# %% Main function


print("Begin VSPAERO Test Analysis\n")

TestAll()

# # ==== Check For API Errors ====#
# while (GetNumTotalErrors() > 0 )
#
#     ErrorObj err = PopLastError()
#     print(err.GetErrorString())
#

print("End VSPAERO Test Analysis")
