"""Run VSPAERO validation test 2."""
import openvsp as vsp
import os
import subprocess

import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

DPI = 300
PALETTE = ["darkblue", "darkorange", "darkgreen", "firebrick",
           "purple", "mediumvioletred", "goldenrod", "darkcyan"]
MARKERS = ["o", "^", "s", "P", "d"]
GRAPHICS_DIR = "graphics"
sns.set_theme(style="whitegrid", font="Palatino Linotype",
              context="paper", palette=PALETTE)

# %% File system

OUTPUTDIR = "output"
VSPSCRIPT = "runVSPAEROSweep.vspscript"
FNAME = "validation_cs_9.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# Wing geometry
midspan = 63.630/12
root_chord = 21.941/12
tip_chord = 9.873/12
sweep_loc = 0.25
sweep = 45

xseccurve_type = 8
tc_rat = 0.12
series = 5

# Mesh parameters
chordwise_tess = 33
spanwise_tess = 24
root_clstr = 1
tip_clstr = 0.5
le_clstr = 0.25
te_clstr = 0.25

# Flow conditions
alpha_i = -5
alpha_f = 15
alpha_npts = 21
alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

# Known results
prcnt_error = 0.05

expalpha_array = np.array([-3.611, -2.6, -1.511, -0.526, -0.111, 0.563, 1.652,
                           2.689, 3.622, 4.659, 5.696, 6.837, 7.719, 8.859,
                           9.793, 10.778, 11.919, 12.904, 13.993, 14.926,
                           15.911, 17, 18.037, 19.022, 20.007, 20.993, 21.952])
expCL_array = np.array([-0.235, -0.177, -0.087, -0.012, 0.027, 0.069, 0.15,
                        0.22, 0.284, 0.36, 0.41, 0.474, 0.544, 0.6, 0.655,
                        0.711, 0.767, 0.809, 0.857, 0.901, 0.951, 1.01, 1.041,
                        1.074, 1.091, 1.099, 1.08])

# %% Create OpenVSP file

vsp.ClearVSPModel()

# Add wing
wing_id = vsp.AddGeom("WING")

# Modify wing
vsp.SetParmValUpdate(wing_id, "Span", "XSec_1", midspan)
vsp.SetParmValUpdate(wing_id, "Root_Chord", "XSec_1", root_chord)
vsp.SetParmValUpdate(wing_id, "Tip_Chord", "XSec_1", tip_chord)
vsp.SetParmValUpdate(wing_id, "Sweep_Location", "XSec_1", sweep_loc)
vsp.SetParmValUpdate(wing_id, "Sweep", "XSec_1", sweep)

xsec_surf = vsp.GetXSecSurf(wing_id, 0)
vsp.ChangeXSecShape(xsec_surf, 0, vsp.XS_SIX_SERIES)
vsp.ChangeXSecShape(xsec_surf, 1, vsp.XS_SIX_SERIES)
vsp.Update()
vsp.SetParmValUpdate(wing_id, "Series", "XSecCurve_0", series)
vsp.SetParmValUpdate(wing_id, "Series", "XSecCurve_1", series)
vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_0", tc_rat)
vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_1", tc_rat)

# Modifiy mesh
vsp.SetParmValUpdate(wing_id, "Tess_W", "Shape", chordwise_tess)
vsp.SetParmValUpdate(wing_id, "SectTess_U", "XSec_1", spanwise_tess)
vsp.SetParmValUpdate(wing_id, "InCluster", "XSec_1", root_clstr)
vsp.SetParmValUpdate(wing_id, "OutCluster", "XSec_1", tip_clstr)
vsp.SetParmValUpdate(wing_id, "LECluster", "WingGeom", le_clstr)
vsp.SetParmValUpdate(wing_id, "TECluster", "WingGeom", te_clstr)
vsp.Update()

vsp.WriteVSPFile(FDIR, vsp.SET_ALL)
vsp.Update()


# %%Define funxtion to set analysis parameters


def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach=0.0):
    with open(VSPAERODIR) as file_object:
        vspscriptlines = file_object.readlines()
    vspscriptlines[10] = '	  string fname = "{0}";\n'.format(FNAME)
    vspscriptlines[47] = "    double alpha_i = {0};\n".format(alpha_i)
    vspscriptlines[52] = "    double alpha_f = {0};\n".format(alpha_f)
    vspscriptlines[57] = "    double alpha_npts = {0};\n".format(alpha_npts)
    vspscriptlines[62] = "    double mach_i = {0:.2f};\n".format(mach)

    with open(VSPAERODIR, "w") as file_object:
        file_object.writelines(vspscriptlines)


# %% Chordwise tesselation sensitivity analysis

setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts)

vsp.ClearVSPModel()
vsp.ReadVSPFile(FDIR)
vsp.Update()

subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)

polar_array = np.loadtxt(
    os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.polar"), skiprows=1)

CL_array = polar_array[:, 4]
CM_array = polar_array[:, 18]


# %% Plot results

fig, ax1 = plt.subplots(1, sharex=True, dpi=DPI)
ax1.plot(alpha_array, CL_array, label="VSPAERO")
ax1.plot(expalpha_array, expCL_array, linestyle="None",
         label="Experimental", color=PALETTE[1], marker=MARKERS[1])
# ax1.fill_between(expalpha_array, expCL_array*(1 + prcnt_error),
#                  expCL_array*(1 - prcnt_error), alpha=0.25,
#                  color=PALETTE[1])
ax1.set_ylim(bottom=-0.4)
ax1.set_xlabel(r"$\mathdefault{\alpha}$, °")
ax1.set_ylabel(r"$\mathdefault{C_{L}}$")
ax1.legend()

fig.savefig(os.path.join(GRAPHICS_DIR, "lift_curve.pdf"), format="pdf",
            bbox_inches="tight")
