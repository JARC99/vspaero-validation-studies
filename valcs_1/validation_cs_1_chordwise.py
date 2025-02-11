"""Run VSPAERO validation test 2."""
import openvsp as vsp
import os
import subprocess
import time

import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

DPI = 300
PALETTE = ["darkblue", "darkorange", "darkgreen", "firebrick",
           "purple", "mediumvioletred", "goldenrod", "darkcyan"]
MARKERS = ["o", "^", "s", "P", "d"]
LEGEND_FONTSIZE = "small"
GRAPHICS_DIR = "graphics"
sns.set_theme(style="whitegrid", font="Times New Roman",
              context="paper", palette=PALETTE)

# %% File system

OUTPUTDIR = "output"
VSPSCRIPT = "runVSPAEROSweep.vspscript"
FNAME = "validation_2.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# Wing geometry
span = 10
chord = 1
sweep = 35
tcrat = 0.09

# Mesh parameters
chordwise_tess_array = np.arange(5.0, 137.0, 8.0)
spanwise_tess = 6
root_clstr = 1
tip_clstr = 0.5
le_clstr = 0.25
te_clstr = 0.25

# Flow conditions
alpha_i = 9
alpha_f = 10
alpha_npts = 2

v_inf = 168.8
a = 1116.45
mach = v_inf/a

# Known results
prcnt_error = 0.05

if sweep == 0:
    DATCOM_dCLdalpha = 0.0885*180/np.pi
    SURFACES_dCLdalpha = 0.0860*180/np.pi
    DATCOM_CL = 0.885
    SURFACES_CL = 0.845
    DATCOM_CDi = 0.0249
    SURFACES_CDi = 0.0227

else:
    DATCOM_dCLdalpha = 0.0748*180/np.pi
    SURFACES_dCLdalpha = 0.07365*180/np.pi
    DATCOM_CL = 0.748
    SURFACES_CL = 0.723
    DATCOM_CDi = 0.0178
    SURFACES_CDi = 0.0166


# %% Create OpenVSP file

vsp.ClearVSPModel()

# Add wing
wing_id = vsp.AddGeom("WING")

# Modify wing
vsp.SetParmValUpdate(wing_id, "TotalSpan", "WingGeom", span)
vsp.SetParmValUpdate(wing_id, "Root_Chord", "XSec_1", chord)
vsp.SetParmValUpdate(wing_id, "Tip_Chord", "XSec_1", chord)
vsp.SetParmValUpdate(wing_id, "Sweep", "XSec_1", sweep)
vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_0", tcrat)
vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_1", tcrat)

# Modifiy mesh
# vsp.SetParmValUpdate(wing_id, "Tess_W", "Shape", chordwise_tes)
vsp.SetParmValUpdate(wing_id, "SectTess_U", "XSec_1", spanwise_tess)
vsp.SetParmValUpdate(wing_id, "InCluster", "XSec_1", root_clstr)
vsp.SetParmValUpdate(wing_id, "OutCluster", "XSec_1", tip_clstr)
vsp.Update()

vsp.WriteVSPFile(FDIR, vsp.SET_ALL)
vsp.Update()


# %%Define funxtion to set analysis parameters


def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach):
    with open(VSPAERODIR) as file_object:
        vspscriptlines = file_object.readlines()
    vspscriptlines[47] = "    double alpha_i = {0};\n".format(alpha_i)
    vspscriptlines[52] = "    double alpha_f = {0};\n".format(alpha_f)
    vspscriptlines[57] = "    double alpha_npts = {0};\n".format(alpha_npts)
    vspscriptlines[62] = "    double mach_i = {0:.2f};\n".format(mach)

    with open(VSPAERODIR, "w") as file_object:
        file_object.writelines(vspscriptlines)


# %% Chordwise tesselation sensitivity analysis

setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach)

CL_list = []
dCLdalpha_list = []
CDi_list = []
time_exec_list = []
for chordwise_tess in chordwise_tess_array:
    vsp.ClearVSPModel()
    vsp.ReadVSPFile(FDIR)

    vsp.SetParmValUpdate(wing_id, "Tess_W", "Shape", chordwise_tess)

    vsp.Update()

    vsp.WriteVSPFile(FDIR, vsp.SET_ALL)
    vsp.Update()

    start = time.time()
    subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)
    end = time.time()

    polar_array = np.loadtxt(
        os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.polar"), skiprows=1)
    CL_list.append(polar_array[1, 4])
    dCLdalpha_list.append(polar_array[1, 4] - polar_array[0, 4])
    CDi_list.append(polar_array[1, 6])
    time_exec_list.append(end - start)

dCLdalpha_list = np.array(dCLdalpha_list)*180/np.pi

# %% Plot results

fig, axes = plt.subplots(4, sharex=True, dpi=DPI)
ax1 = axes[0]
ax2 = axes[1]
ax3 = axes[2]
ax4 = axes[3]

ax4.set_xlabel("Chordwise Tesselation")

ax1.set_ylabel(r"$\mathdefault{C_{L_{\alpha}},~rad^{-1}}$")
ax2.set_ylabel(r"$\mathdefault{C_{L}}$")
ax3.set_ylabel(r"$\mathdefault{C_{D_{i}}}$")
ax4.set_ylabel("Time, s")

ax1.plot(chordwise_tess_array, dCLdalpha_list, linestyle="None",
         marker=MARKERS[0], color=PALETTE[0], label="VSPAERO")
# ax1.errorbar(chordwise_tess_array, dCLdalpha_list, yerr=np.array(
#     dCLdalpha_list)*prcnt_error, linestyle="None", marker=MARKERS[0], ecolor="black", capsize=3)
ax1.axhline(DATCOM_dCLdalpha,
            color=PALETTE[1], linestyle="dashed", label=r"$\mathdefault{DATCOM~\pm 5\%}$")
ax1.axhspan(DATCOM_dCLdalpha*(1-prcnt_error), DATCOM_dCLdalpha *
            (1+prcnt_error), color=PALETTE[1], alpha=0.25)
ax1.axhline(SURFACES_dCLdalpha,
            color=PALETTE[2], linestyle="dashed", label="SURFACES")



#ax1.legend(loc="upper left", ncol=3)

ax2.plot(chordwise_tess_array, CL_list, linestyle="None",
         marker=MARKERS[0], color=PALETTE[0], label="VSPAERO")
# ax2.errorbar(chordwise_tess_array, CL_list, yerr=np.array(
#     CL_list)*prcnt_error, label="VSPAERO", linestyle="None", marker=MARKERS[0], ecolor="black", capsize=3)
ax2.axhline(DATCOM_CL, color=PALETTE[1], linestyle="dashed")
ax2.axhspan(DATCOM_CL*(1-prcnt_error), DATCOM_CL *
            (1+prcnt_error), color=PALETTE[1], alpha=0.25)
ax2.axhline(SURFACES_CL, color=PALETTE[2], linestyle="dashed")


ax3.plot(chordwise_tess_array, CDi_list, linestyle="None",
         marker=MARKERS[0], color=PALETTE[0], label="VSPAERO")
# ax3.errorbar(chordwise_tess_array, CDi_list, yerr=np.array(
#     CDi_list)*prcnt_error, label="VSPAERO", linestyle="None", marker=MARKERS[0], ecolor="black", capsize=3)
ax3.axhline(DATCOM_CDi, color=PALETTE[1], linestyle="dashed", label="DATCOM")
ax3.axhspan(DATCOM_CDi*(1-prcnt_error), DATCOM_CDi *
            (1+prcnt_error), color=PALETTE[1], alpha=0.25)
ax3.axhline(SURFACES_CDi, color=PALETTE[2],
            linestyle="dashed", label="SURFACES")


ax4.plot(chordwise_tess_array, time_exec_list, color=PALETTE[0], label="VSPAERO")
# ax3.errorbar(chordwise_tess_array, CDi_list, yerr=np.array(
#     CDi_list)*prcnt_error, label="VSPAERO", linestyle="None", marker=MARKERS[0], ecolor="black", capsize=3)

ax1.set_xlim(left=0)

ax1.set_ylim(3.75, 4.75)
ax2.set_ylim(0.65, 0.85)
ax3.set_ylim(0.015, 0.02)
ax4.set_ylim(bottom=0, top=9)



fig.align_ylabels()
fig.savefig(os.path.join(GRAPHICS_DIR, "chordwise_sweep-{0}deg.pdf".format(sweep)),
            format="pdf", bbox_inches="tight")
