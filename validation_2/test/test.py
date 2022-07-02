import openvsp as vsp

print("-> Begin TestVSPAeroSharpTrailingEdge\n")

# ==== Analysis: VSPAero Single Point ====
analysis_name = "VSPAEROSinglePoint"
print(analysis_name)

# ==== Create some test geometries ====
print("--> Generating Geometries\n")

wing_id = vsp.AddGeom("WING", "")

# Get Section IDs
wingxsurf_id = vsp.GetXSecSurf(wing_id, 0)
xsec_id0 = vsp.GetXSec(wingxsurf_id, 0)
xsec_id1 = vsp.GetXSec(wingxsurf_id, 1)

# Set Root and Tip Chord to 3:
vsp.SetDriverGroup(wing_id, 1, vsp.AREA_WSECT_DRIVER,
                   vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
vsp.SetParmVal(wing_id, "Root_Chord", "XSec_1", 3.0)
vsp.SetParmVal(wing_id, "Tip_Chord", "XSec_1", 3.0)
vsp.SetParmVal(wing_id, "Area", "XSec_1", 25.0)

# Set Sweep to 0:
xsweep_id1 = vsp.GetXSecParm(xsec_id1, "Sweep")
vsp.SetParmVal(xsweep_id1, 0.0)

# Increase W Tesselation:
vsp.SetParmVal(wing_id, "Tess_W", "Shape", 20)

# Increase U Tesselation
xutess_id1 = vsp.GetXSecParm(xsec_id1, "SectTess_U")
vsp.SetParmVal(xutess_id1, 16)

vsp.Update()

# ==== Save Vehicle to File ====
print("-->Saving VSP model\n")
fname = "TestVSPAeroSharpTrailingEdge.vsp3"
vsp.WriteVSPFile(fname, vsp.SET_ALL)
vsp.Update()

# Close and open the file
vsp.ClearVSPModel()
vsp.Update()
vsp.ReadVSPFile(fname)   # Sets VSP3 file name
vsp.Update()

# ==== Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File ====
compgeom_name = "VSSPAEROComputeGeometry"
print(compgeom_name)

# Set defaults
vsp.SetAnalysisInputDefaults(compgeom_name)

# analysis_method = list(vsp.GetIntAnalysisInput(
#     compgeom_name, "AnalysisMethod"))
# analysis_method[0] = vsp.VORTEX_LATTICE
# vsp.SetIntAnalysisInput(compgeom_name, "AnalysisMethod", analysis_method)

# list inputs, type, and current values
vsp.PrintAnalysisInputs(compgeom_name)

# Execute
print("\tExecuting...")
compgeom_resid = vsp.ExecAnalysis(compgeom_name)
print("COMPLETE")

# Get & Display Results
vsp.PrintResults(compgeom_resid)


# ==== Analysis: VSPAero Single Point ====
# Set defaults
vsp.SetAnalysisInputDefaults(analysis_name)

# Reference geometry set
# geom_set = []
# geom_set.append(0)
# vsp.SetIntAnalysisInput(analysis_name, "GeomSet", geom_set, 0)
# ref_flag = []
# ref_flag.append(1)
# vsp.SetIntAnalysisInput(analysis_name, "RefFlag", ref_flag, 0)
# wid = vsp.FindGeomsWithName("WingGeom")
# vsp.SetStringAnalysisInput(analysis_name, "WingID", wid, 0)

# # Freestream Parameters
# alpha = []
# alpha.append(3.25)
# vsp.SetDoubleAnalysisInput(analysis_name, "Alpha", alpha, 0)
# mach = []
# mach.append(0.12)
# vsp.SetDoubleAnalysisInput(analysis_name, "Mach", mach, 0)

# vsp.Update()

# # list inputs, type, and current values
# vsp.PrintAnalysisInputs(analysis_name)
# print("")
# #%%
# # Execute
# print("\tExecuting...")
# rid = vsp.ExecAnalysis(analysis_name)
# print("COMPLETE")

# # Get & Display Results
# vsp.PrintResults(rid)

# history_res = vsp.FindLatestResultsID("VSPAERO_History")
# load_res = vsp.FindLatestResultsID("VSPAERO_Load")

# CL = vsp.GetDoubleResults(history_res, "CL", 0)
# cl = vsp.GetDoubleResults(load_res, "cl", 0)

# # print("CL at 0 angle of attack: ", false)

# # for (int i = 0 i < int(CL.size()) i ++ )
# # {
# #     print(CL[i], false)
# # }
# # print("")

# # print("cl at 0 angle of attack: ", false)
# # for (int j = 0 j < int(cl.size()) j ++ )
# # {
# #     print(cl[j], false)
# # }
# # print("")
# # print("")
