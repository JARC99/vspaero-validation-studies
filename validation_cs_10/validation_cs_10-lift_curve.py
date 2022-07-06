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
FNAME = "validation_cs_10.vsp3"
FDIR = os.path.join(OUTPUTDIR, FNAME)
VSPAERODIR = os.path.join(OUTPUTDIR, VSPSCRIPT)


# %% User input

# Wing geometry
midspan = 180/2/12
root_chord = 28.57/12
tip_chord = 11.43/12
sweep_loc = 0.25
sweep = 0
dihedral = 3
tipmatchdhdrl_flag = True
twist_array = np.array([0.0, -2.0])

tap_rat = tip_chord/root_chord
chord_mgc = 2/3 * root_chord * (1 + tap_rat + tap_rat**2)/(1 + tap_rat)
yloc_mgc = midspan/3 * (1 + 2*tap_rat)/(1 + tap_rat)
xloc_mgc = yloc_mgc*np.tan(sweep*np.pi/180) + chord_mgc/4

xseccurve_type = vsp.XS_SIX_SERIES
tc_rat = 0.10
series = 2
cl_i = 0.2

# Mesh parameters
chordwise_tess = 33
spanwise_tess = 24
root_clstr = 1
tip_clstr = 0.5
le_clstr = 0.25
te_clstr = 0.25

# Flow conditions
alpha_i = -3
alpha_f = 13
alpha_npts = 17
alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

mach = 0.17

# Known results
prcnt_error = 0.05

x_wsh0 = [-2.960000000000001, -1.8400000000000056, -0.8800000000000026,
          0.1599999999999966, 1.1999999999999957, 2.239999999999995,
          3.4399999999999906, 4.47999999999999, 5.519999999999989,
          6.63999999999999, 7.679999999999989, 8.639999999999986,
          9.759999999999982, 10.879999999999981, 11.439999999999982,
          11.999999999999982, 12.479999999999976, 12.95999999999998,
          13.599999999999977, 13.999999999999975]
y_wsh0 = [-0.14799999999999985, -0.05599999999999999, 0.03599999999999989,
          0.12000000000000008, 0.21600000000000022, 0.31600000000000006,
          0.39933331298828134, 0.4833333129882811, 0.5833333129882812,
          0.6673333129882814, 0.7673333129882813, 0.8593333129882812,
          0.9593333129882812, 1.031333312988281, 1.079333312988281,
          1.119333312988281, 1.163333312988281, 1.203333312988281,
          1.239333312988281, 1.0873333129882812]
expCL_wsh0 = np.array([x_wsh0, y_wsh0]).T

x_wsh2 = [-2.988142292490118, -1.9920948616600789, -0.9486166007905138,
          0.23715415019762845, 1.233201581027668, 2.276679841897233,
          3.4150197628458496, 4.411067193675889, 5.50197628458498,
          6.4980237154150196, 6.545454545454545, 7.541501976284584,
          8.632411067193676, 9.723320158102766, 10.861660079051383,
          11.288537549407113, 12.42687747035573, 12.901185770750986,
          13.42292490118577, 14.039525691699604, 14.466403162055334]
y_wsh2 = [-0.174390243902439, -0.08414634146341464, 0.013414634146341461,
          0.10365853658536583, 0.19878048780487803, 0.28414634146341466,
          0.38170731707317074, 0.4670731707317073, 0.5658536585365854,
          0.6487804878048781, 0.6707317073170732, 0.7463414634146341,
          0.8439024390243902, 0.9317073170731708, 1.0219512195121951,
          1.073170731707317, 1.1536585365853658, 1.1926829268292682,
          1.226829268292683, 1.2317073170731707, 1.1317073170731706]
expCL_wsh2 = np.array([x_wsh2, y_wsh2]).T

expCL_array_list = [expCL_wsh0, expCL_wsh2]


# %%Define funxtion to set analysis parameters


def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach=0.0, x_cg=0.0,
                         y_cg=0.0, z_cg=0.0):
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


# %% Create OpenVSP file

fig, ax1 = plt.subplots(1, sharey=True, dpi=DPI)
for i, twist in enumerate(twist_array):
    vsp.ClearVSPModel()

    # Add wing
    wing_id = vsp.AddGeom("WING")

    # Modify wing
    vsp.SetParmValUpdate(wing_id, "Span", "XSec_1", midspan)
    vsp.SetParmValUpdate(wing_id, "Root_Chord", "XSec_1", root_chord)
    vsp.SetParmValUpdate(wing_id, "Tip_Chord", "XSec_1", tip_chord)
    vsp.SetParmValUpdate(wing_id, "Sweep_Location", "XSec_1", sweep_loc)
    vsp.SetParmValUpdate(wing_id, "Sweep", "XSec_1", sweep)
    vsp.SetParmValUpdate(wing_id, "Dihedral", "XSec_1", dihedral)
    vsp.SetParmValUpdate(wing_id, "Twist", "XSec_1", twist)
    vsp.SetParmValUpdate(wing_id, "RotateMatchDideralFlag",
                         "XSec_1", tipmatchdhdrl_flag)

    xsec_surf = vsp.GetXSecSurf(wing_id, 0)
    vsp.ChangeXSecShape(xsec_surf, 0, xseccurve_type)
    vsp.ChangeXSecShape(xsec_surf, 1, xseccurve_type)
    vsp.Update()
    vsp.SetParmValUpdate(wing_id, "Series", "XSecCurve_0", series)
    vsp.SetParmValUpdate(wing_id, "Series", "XSecCurve_1", series)
    vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_0", tc_rat)
    vsp.SetParmValUpdate(wing_id, "ThickChord", "XSecCurve_1", tc_rat)
    vsp.SetParmValUpdate(wing_id, "IdealCl", "XSecCurve_0", cl_i)
    vsp.SetParmValUpdate(wing_id, "IdealCl", "XSecCurve_1", cl_i)

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

    setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts,
                         mach=mach, x_cg=xloc_mgc)

    vsp.ClearVSPModel()
    vsp.ReadVSPFile(FDIR)
    vsp.Update()

    subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)

    polar_array = np.loadtxt(
        os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.polar"), skiprows=1)

    CL_array = polar_array[:, 4]
    CM_array = polar_array[:, 18]

# Plot results

    ax1.plot(alpha_array, CL_array,
             label="VSPAERO, " + r"$\mathdefault{\phi_{G}}=$" +
             "{0}°".format(int(twist)))
    ax1.plot(expCL_array_list[i][:, 0], expCL_array_list[i][:, 1],
             linestyle="None", color=PALETTE[i], marker=MARKERS[1],
             label="Experimental, " +
             r"$\mathdefault{\phi_{G}}=$" + "{0}°".format(int(twist)))
    # ax1.fill_between(expCL_array_list[i][:, 0],
                     # expCL_array_list[i][:, 1]*(1 + prcnt_error),
                     # expCL_array_list[i][:, 1]*(1 - prcnt_error), alpha=0.25,
                     # color=PALETTE[i])
    # ax1.set_ylim(bottom=-0.4)
    ax1.set_xlabel(r"$\mathdefault{\alpha}$, °")
    ax1.set_ylabel(r"$\mathdefault{C_{L}}$")
    ax1.legend()

    fig.savefig(os.path.join(GRAPHICS_DIR, "lift_curves.pdf"), format="pdf",
                bbox_inches="tight")

# %%

    # fig, ax1 = plt.subplots(1, sharex=True, dpi=DPI)
    # ax1.plot(CL_array, CM_array, label="VSPAERO")
    # # ax1.plot(expCL4CM_array, expCM_array, linestyle="None",
    # #          label="Experimental", color=PALETTE[1], marker=MARKERS[1])
    # # ax1.fill_between(expalpha_array, expCL_array*(1 + prcnt_error),
    # #                  expCL_array*(1 - prcnt_error), alpha=0.25,
    # #                  color=PALETTE[1])
    # #ax1.set_xlim(left=-0.4, right=1.0)
    # #ax1.set_ylim(bottom=-0.15)

    # ax1.set_xlabel(r"$\mathdefault{C_{L}}$")
    # ax1.set_ylabel(r"$\mathdefault{C_{M}}$")
    # ax1.legend()
    # fig.savefig(os.path.join(GRAPHICS_DIR, "moment_curves.pdf"), format="pdf",
    #             bbox_inches="tight")