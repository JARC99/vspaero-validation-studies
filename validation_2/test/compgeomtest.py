"""Run VSPAERO validation test 2."""
import openvsp as vsp
import os

OUTPUT_DIR = ""
fname = "compgeomtest_2.vsp3"
fdir = os.path.join(OUTPUT_DIR, fname)

#%%

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
vsp.WriteVSPFile(fdir)
print("COMPLETE\n")
vsp.Update()

vsp.ClearVSPModel()

#%%
print("-> Begin TestVSPAeroComputeGeom")
print("")

#  open the file created in GenerateGeom
fname_vspaerotests = fdir
vsp.ReadVSPFile(fname_vspaerotests)  # Sets VSP3 file name

# ==== Analysis: VSPAero Compute Geometry ====#
analysis_name = "VSPAEROComputeGeometry"
print(analysis_name)

#  Set defaults
vsp.SetAnalysisInputDefaults(analysis_name)

#  Analysis method
analysis_method = list(vsp.GetIntAnalysisInput(
    analysis_name, "AnalysisMethod"))
analysis_method[0] = vsp.VORTEX_LATTICE
vsp.SetIntAnalysisInput(analysis_name, "AnalysisMethod", analysis_method)

#  list inputs, type, and current values


#%%
#  Execute
print("\tExecuting...")
rid = vsp.ExecAnalysis(analysis_name)
print("COMPLETE")

#  Get & Display Results
