"""Run VSPAERO validation test A."""
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
GRAPHICS_DIR = "graphics"
sns.set_theme(style="whitegrid", font="Times New Roman",
              context="paper", palette=PALETTE)

# %% File system

OUTPUTDIR = "output"
DATADIR = "data"
VSPSCRIPT = "runVSPAEROSweep.vspscript"
FNAME = "valcs_7.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# WIng geometry
AR = 4.0
chord_mgc = 3.5/12
sweep = 0
sweep_loc = 0.25

wing_TR50 = [13.5/12, 0.5]
wing_TR75 = [13.91/12, 0.75]
wing_TR100 = [14/12, 1.0]
wing_list = [wing_TR50, wing_TR75, wing_TR100]

# Mesh parameters
chordwise_tess = 33
spanwise_tess = 24
root_clstr = 1
tip_clstr = 0.5
le_clstr = 0.25
te_clstr = 0.25

# Flow conditions
alpha_i = -10
alpha_f = 10
alpha_npts = 3
alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

# Known results
prcnt_error = 0.05


# %%Define funxtion to set analysis parameters

def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach=0.0, x_cg=0.0,
                         y_cg=0.0, z_cg=0.0,
                         chord_mgc=chord_mgc):
    with open(VSPAERODIR) as file_object:
        vspscriptlines = file_object.readlines()
    vspscriptlines[10] = '	  string fname = "{0}";\n'.format(FNAME)
    vspscriptlines[47] = "    double alpha_i = {0};\n".format(alpha_i)
    vspscriptlines[52] = "    double alpha_f = {0};\n".format(alpha_f)
    vspscriptlines[57] = "    double alpha_npts = {0};\n".format(alpha_npts)
    vspscriptlines[62] = "    double mach_i = {0:.2f};\n".format(mach)

    vspscriptlines[68] = "    double x_cg = {0:.3f};\n".format(x_cg)
    vspscriptlines[73] = "    double y_cg = {0:.3f};\n".format(y_cg)
    vspscriptlines[78] = "    double z_cg = {0:.3f};\n".format(z_cg)

    vspscriptlines[84] = "    double chord_mgc = {0:.3f};\n".format(chord_mgc)

    with open(VSPAERODIR, "w") as file_object:
        file_object.writelines(vspscriptlines)


# %% Create OpenVSP file

fig1, ax1 = plt.subplots(1, sharex=True, dpi=DPI)
ax1 = ax1

#fig2, ax2 = plt.subplots(1, sharex=True, dpi=DPI)
for i, wing in enumerate(wing_list):
    vsp.ClearVSPModel()

    # Add wing
    wing_id = vsp.AddGeom("WING")

    # Modify wing
    vsp.SetDriverGroup(wing_id, 1, vsp.AR_WSECT_DRIVER,
                       vsp.TAPER_WSECT_DRIVER, vsp.SPAN_WSECT_DRIVER)
    vsp.SetParmValUpdate(wing_id, "Aspect", "XSec_1", AR/2)
    vsp.SetParmValUpdate(wing_id, "Span", "XSec_1", wing[0]/2)
    vsp.SetParmValUpdate(wing_id, "Taper", "XSec_1", wing[1])
    vsp.SetParmValUpdate(wing_id, "Sweep_Location", "XSec_1", sweep_loc)
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

    setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, chord_mgc=chord_mgc)

    vsp.ClearVSPModel()
    vsp.ReadVSPFile(FDIR)
    vsp.Update()

    subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)

    polar_array = np.loadtxt(
        os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.polar"), skiprows=1)

    CL_array = polar_array[:, 4]
    CM_array = polar_array[:, 18]


# %%

    # Known results
    datafile = os.path.join(DATADIR, "TR{0}.dat".format(int(wing[1]*100)))
    exppolar_array = np.loadtxt(datafile, skiprows=1)
    exppolar_array = exppolar_array[np.lexsort(
        (exppolar_array[:, 1], exppolar_array[:, 0]))][::2, :]
    expCL_array = exppolar_array[:, 1]
    expalpha_array = exppolar_array[:, 0]


# %% Plot results

    ax1.plot(alpha_array, CL_array, label="VSPAERO, " +
             r"$\mathdefault{\lambda = }$" + str(wing[1]))
    ax1.plot(expalpha_array, expCL_array, linestyle="None", label="Experimental, " +
             r"$\mathdefault{\lambda = }$" + str(wing[1]), color=PALETTE[i], marker=MARKERS[1], alpha=0.5)

#%% Calculate the percent error

    expCLfromalpha = interpolate.interp1d(
        expalpha_array, expCL_array, fill_value="extrapolate")
    expCL4error = expCLfromalpha(alpha_array)

    expdCLdalpha = np.mean((expCL4error[1:] - expCL4error[:-1])/(alpha_array[1] - alpha_array[0])) * 180/np.pi
    dCLdalpha = np.mean((CL_array[1:] - CL_array[:-1])/(alpha_array[1] - alpha_array[0])) * 180/np.pi
    dCLdalpha_error = np.abs((dCLdalpha - expdCLdalpha)/expdCLdalpha) * 100
    print("Experimental dCL/dalpha = {0}".format(round(expdCLdalpha, 4)))
    print("VSPAERO dCL/dalpha = {0}".format(round(dCLdalpha, 4)))
    print("% Error = {0}".format(round(dCLdalpha_error, 2)))
    print("-----------------------------------------\n")


ax1.set_xlabel("Angle of Attack, °")
ax1.set_ylabel("Lift Coefficient")
ax1.legend()
fig1.savefig(os.path.join(GRAPHICS_DIR, "lift_curves.pdf"), format="pdf",
              bbox_inches="tight")
