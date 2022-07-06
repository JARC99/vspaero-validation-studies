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
LEGEND_FONTSIZE = "small"
GRAPHICS_DIR = "graphics"
sns.set_theme(style="whitegrid", font="Palatino Linotype",
              context="paper", palette=PALETTE)

# %% File system

OUTPUTDIR = "output"
VSPSCRIPT = "runVSPAEROSweep.vspscript"
FNAME = "validation_cs_4.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# Wing geometry
span = 1.0
root_chord = 0.2
tip_chord = 0.2
sweep = 45

# Mesh parameters
chordwise_tess = 33
spanwise_tess = 24
root_clstr = 1
tip_clstr = 0.5
le_clstr = 0.25
te_clstr = 0.25

# Flow conditions
alpha_i = 0
alpha_f = 10
alpha_npts = 11
alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

v_inf = 1
a = 1116.45
mach = v_inf/a

# Known results
prcnt_error = 0.05

knowndCLdalpha_list = [3.433, 3.442, 3.450]  # , 2.790, 2.776, 2.767]
# , "SURFACES 6x16", "SURFACES 8x24", "SURFACES 16x36"]
knownlabel_list = [r"$\mathdefault{Bertin-Smith~\pm 5\%}$", "SURFACES", "Tornado"]

# %% Create OpenVSP file

vsp.ClearVSPModel()

# Add wing
wing_id = vsp.AddGeom("WING")

# Modify wing
vsp.SetParmValUpdate(wing_id, "TotalSpan", "WingGeom", span)
vsp.SetParmValUpdate(wing_id, "Root_Chord", "XSec_1", root_chord)
vsp.SetParmValUpdate(wing_id, "Tip_Chord", "XSec_1", tip_chord)
vsp.SetParmValUpdate(wing_id, "Sweep", "XSec_1", sweep)

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


def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach):
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

setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach)

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

ax1.set_xlabel(r"$\mathdefault{\alpha}$, °")

ax1.set_ylabel(r"$\mathdefault{C_{L}}$")

ax1.plot(alpha_array, CL_array, marker=MARKERS[0], label="VSPAERO")
for i, knownlabel in enumerate(knownlabel_list):
    knownCL_array = knowndCLdalpha_list[i]*np.pi/180*alpha_array
    ax1.plot(alpha_array, knownCL_array, linestyle="dashed",
             label=knownlabel, color=PALETTE[i+1])


    if not i:
        ax1.fill_between(alpha_array, knownCL_array*(1 + prcnt_error),
                     knownCL_array*(1 - prcnt_error), alpha=0.25, color=PALETTE[i+1])
    else:
        pass



ax1.set_xlim(left=0)
ax1.set_ylim(bottom=0)

ax1.legend(fontsize=LEGEND_FONTSIZE)

fig.savefig(os.path.join(GRAPHICS_DIR, "lift_curve.pdf".format(sweep)),
            format="pdf", bbox_inches="tight")
