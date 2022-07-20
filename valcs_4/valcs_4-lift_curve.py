"""Run VSPAERO validation test 2."""
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
VSPSCRIPT = "runVSPAEROSweep.vspscript"
FNAME = "valcs_4.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# Wing geometry
midspan = 63.630/12
root_chord = 21.941/12
tip_chord = 9.873/12
sweep_loc = 0.25
sweep = 45
sweep_le = 46.33

tap_rat = tip_chord/root_chord
chord_mgc = 2/3 * root_chord * (1 + tap_rat + tap_rat**2)/(1 + tap_rat)
yloc_mgc = midspan/3 * (1 + 2*tap_rat)/(1 + tap_rat)
xloc_mgc = yloc_mgc*np.tan(sweep_le*np.pi/180) + chord_mgc/4

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

expCL4CM_array = np.array([-0.24055562337239586, 0.6894443766276042,
                           -0.17388895670572918, -0.09388895670572918,
                           -0.09388895670572918, 0.9138333129882813,
                           0.8671666463216147, 0.8138333129882813,
                           0.7738333129882813, 0.7271666463216147,
                           0.6338333129882813, 0.5904999796549479,
                           0.5338333129882813, 0.49049997965494796,
                           -0.09433334350585938, 0.1171666463216146,
                           0.1671666463216146, 0.24049997965494793,
                           0.3171666463216146, 0.42049997965494795,
                           0.25383331298828127])
expCM_array = np.array([0.013559322033898306, 0.030508474576271188,
                        0.01016949152542373, 0.010847457627118645,
                        0.010847457627118645, 0.09966101694915255,
                        0.08542372881355932, 0.07932203389830508,
                        0.058983050847457634, 0.04949152542372882,
                        0.015593220338983051, 0.0033898305084745766,
                        -0.002711864406779661, -0.007457627118644068,
                        0.010847457627118645, -0.008813559322033898,
                        -0.014237288135593221, -0.02169491525423729,
                        -0.018305084745762715, -0.012881355932203391,
                        -0.016271186440677966])

expCMcomb_array = np.vstack((expCL4CM_array, expCM_array)).T
expCMcomb_array = expCMcomb_array[expCMcomb_array[:, 0].argsort()]

expCL4CM_array = np.delete(expCMcomb_array[:, 0], [3, 4])
expCM_array = np.delete(expCMcomb_array[:, 1], [3, 4])

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

setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, x_cg=xloc_mgc)

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
         label="Experimental", color=PALETTE[1], marker=MARKERS[1], alpha=0.5)
# ax1.fill_between(expalpha_array, expCL_array*(1 + prcnt_error),
#                  expCL_array*(1 - prcnt_error), alpha=0.25,
#                  color=PALETTE[1])
ax1.set_ylim(bottom=-0.4)
ax1.set_xlabel("Angle of Attack, °")
ax1.set_ylabel("Lift Coefficient")
ax1.legend()

fig.savefig(os.path.join(GRAPHICS_DIR, "lift_curve.pdf"), format="pdf",
            bbox_inches="tight")



fig, ax1 = plt.subplots(1, sharex=True, dpi=DPI)
ax1.plot(CL_array, CM_array, label="VSPAERO")
ax1.plot(expCL4CM_array, expCM_array, linestyle="None",
         label="Experimental", color=PALETTE[1], marker=MARKERS[1], alpha=0.5)
# ax1.fill_between(expalpha_array, expCL_array*(1 + prcnt_error),
#                  expCL_array*(1 - prcnt_error), alpha=0.25,
#                  color=PALETTE[1])
ax1.set_xlim(left=-0.4, right=1)
ax1.set_ylim(bottom=-0.15)

ax1.set_xlabel("Lift Coefficient")
ax1.set_ylabel("Pitching Moment Coefficient")
#ax1.legend()
fig.savefig(os.path.join(GRAPHICS_DIR, "moment_curve.pdf"), format="pdf",
            bbox_inches="tight")

# %% Error calculation

expCLfromalpha = interpolate.interp1d(expalpha_array, expCL_array, fill_value="extrapolate")
expCL4error = expCLfromalpha(alpha_array)

expdCLdalpha = np.mean(expCL4error[1:] - expCL4error[:-1]) * 180/np.pi
dCLdalpha = np.mean(CL_array[1:] - CL_array[:-1]) * 180/np.pi
dCLdalpha_error = np.abs((dCLdalpha - expdCLdalpha)/expdCLdalpha) * 100
print(dCLdalpha_error)

CL4error_array = np.linspace(-0.25, 0.25, 10)

expCMfromCL = interpolate.interp1d(expCL4CM_array, expCM_array, fill_value="extrapolate")
expCM4error = expCMfromCL(CL4error_array)
expdCMdCL = np.mean((expCM4error[1:] - expCM4error[:-1])/(CL4error_array[1:] - CL4error_array[:-1]))


CMfromCL = interpolate.interp1d(CL_array, CM_array, fill_value="extrapolate")
CM4error = CMfromCL(CL4error_array)
dCMdCL = np.mean((CM4error[1:] - CM4error[:-1])/(CL4error_array[1:] - CL4error_array[:-1]))

dCMdCL_error = np.abs((dCMdCL - expdCMdCL)/expdCMdCL) * 100
print(dCMdCL_error)
