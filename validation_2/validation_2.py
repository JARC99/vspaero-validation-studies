"""Run VSPAERO validation test 2."""
import openvsp as vsp

# %% User input

# Wing geometry
span = 10
chord = 1
sweep = 0

# Mesh parameters
chordwise_tes = 50
spanwise_tes = 20
root_clstr = 1
tip_clstr = 0.5


# %% Create OpenVSP file

vsp.ClearVSPModel()
fname = "validation_2.vsp3"
vsp.SetVSP3FileName(fname)

# Add wing
wing_id = vsp.AddGeom("WING")

# Modify wing
vsp.SetParmValUpdate(wing_id, "TotalSpan", "WingGeom", span)
vsp.SetParmValUpdate(wing_id, "Root_Chord", "XSec_1", chord)
vsp.SetParmValUpdate(wing_id, "Tip_Chord", "XSec_1", chord)
vsp.SetParmValUpdate(wing_id, "Sweep", "XSec_1", sweep)

# Modifiy mesh
vsp.SetParmValUpdate(wing_id, "Tess_W", "Shape", chordwise_tes)
vsp.SetParmValUpdate(wing_id, "SectTess_U", "XSec_1", spanwise_tes)
vsp.SetParmValUpdate(wing_id, "InCluster", "XSec_1", root_clstr)
vsp.SetParmValUpdate(wing_id, "OutCluster", "XSec_1", tip_clstr)

vsp.Update()
vsp.WriteVSPFile(vsp.GetVSPFileName())
