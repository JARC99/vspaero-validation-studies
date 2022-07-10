"""Run VSPAERO validation test 9."""
import openvsp as vsp
import os
import subprocess

import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

from scipy import interpolate

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
alpha_i = 4.7
alpha_f = 5
alpha_npts = 1
alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

# Known results
prcnt_error = 0.05

expyloc_array = np.array(
    [0.001, 0.03, 0.101, 0.301, 0.547, 0.748, 0.899, 0.96])
excldist_array = np.array(
    [1.057, 1.073, 1.156, 1.149, 1.067, 0.908, 0.765, 0.584])


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


def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach=0.0, x_cg=0.0, y_cg=0.0, z_cg=0.0):
    with open(VSPAERODIR) as file_object:
        vspscriptlines = file_object.readlines()
    vspscriptlines[10] = '	  string fname = "{0}";\n'.format(FNAME)
    vspscriptlines[47] = "    double alpha_i = {0};\n".format(alpha_i)
    vspscriptlines[52] = "    double alpha_f = {0};\n".format(alpha_f)
    vspscriptlines[57] = "    double alpha_npts = {0};\n".format(alpha_npts)
    vspscriptlines[62] = "    double mach_i = {0:.2f};\n".format(mach)

    vspscriptlines[68] = "    double x_cg = {0:.2f};\n".format(x_cg)
    vspscriptlines[73] = "    double y_cg = {0:.2f};\n".format(y_cg)
    vspscriptlines[78] = "    double z_cg = {0:.2f};\n".format(z_cg)

    with open(VSPAERODIR, "w") as file_object:
        file_object.writelines(vspscriptlines)


# %% Chordwise tesselation sensitivity analysis

setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts)

vsp.ClearVSPModel()
vsp.ReadVSPFile(FDIR)
vsp.Update()

subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)


# %% Extract load distribution data

loaddist_array = np.loadtxt(
    os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.lod"), skiprows=19,
    max_rows=spanwise_tess-1)

refgeom_array = np.loadtxt(
    os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.lod"), skiprows=3,
    max_rows=14, usecols=1)

polar_array = np.loadtxt(
    os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.polar"), skiprows=1)

cldist_vsp = loaddist_array[:, 7]
yloc_array = loaddist_array[:, 1]
chord_array = loaddist_array[:, 5]
cref = refgeom_array[1]
CL = polar_array[4]
newcldist = cldist_vsp*chord_array/(cref*CL)


# %% Plot results

fig, ax1 = plt.subplots(1, sharex=True, dpi=DPI)
ax1.plot(yloc_array, newcldist, label="VSPAERO")
ax1.plot(expyloc_array, excldist_array, linestyle="None",
         color=PALETTE[1], marker=MARKERS[1], label="Experimental")
# ax1.fill_between(expyloc_array, excldist_array*(1 + prcnt_error),
#                  excldist_array*(1 - prcnt_error), alpha=0.25,
#                  color=PALETTE[1])
ax1.set_xlim(left=0)
ax1.set_ylim(bottom=0)
ax1.set_xlabel(r"$\mathdefault{\dfrac{2y}{b}}$")
ax1.set_ylabel(r"$\mathdefault{\dfrac{c_{L}\bullet c}{C_{L}\bullet c_{ref}}}$")
ax1.legend()

fig.savefig(os.path.join(GRAPHICS_DIR, "lift_dist.pdf"), format="pdf",
            bbox_inches="tight")

# %% Error calculation

cLfromyloc = interpolate.interp1d(
    expyloc_array, excldist_array, fill_value="extrapolate")
expcL4error = cLfromyloc(yloc_array)

cLdist_error = np.mean(np.abs((newcldist - expcL4error)/expcL4error) * 100)
print(cLdist_error)
