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
FNAME = "valcs_5.vsp3"
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
xloc_mgc = root_chord/4
zloc_mgc = 0.025

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

alpha_max_list = [13.599999999999977, 13.42292490118577]


mach = 0.17

# Known results
prcnt_error = 0.05

yloc_wsh0 = [-0.00101010101010101, 0.050505050505050504, 0.1,
             0.1494949494949495, 0.198989898989899, 0.2494949494949495, 0.3,
             0.34949494949494947, 0.398989898989899, 0.4505050505050505,
             0.498989898989899, 0.5484848484848485, 0.6, 0.6494949494949495,
             0.6989898989898989, 0.7494949494949495, 0.798989898989899,
             0.8494949494949495, 0.9, 0.9494949494949495, 0.9282828282828283,
             0.9666666666666667, 0.9777777777777777, 0.9878787878787879]
cL_wsh0 = [1.1524752475247524, 1.1702970297029702, 1.194059405940594,
           1.2099009900990099, 1.2198019801980198, 1.2356435643564356,
           1.2435643564356436, 1.2554455445544555, 1.2613861386138614,
           1.2673267326732673, 1.2732673267326733, 1.2752475247524753,
           1.2752475247524753, 1.2732673267326733, 1.2673267326732673,
           1.2594059405940594, 1.2415841584158416, 1.205940594059406,
           1.1405940594059405, 0.9722772277227723, 1.0673267326732674,
           0.8574257425742575, 0.7683168316831683, 0.6534653465346536]
cLdist_wsh0 = np.array([yloc_wsh0, cL_wsh0]).T


yloc_wsh2 = [-0.002167182662538708, 0.04891640866873065, 0.09814241486068112,
             0.14922600619195048, 0.20030959752321983, 0.25046439628482975,
             0.29876160990712075, 0.34984520123839014, 0.39907120743034064,
             0.4510835913312694, 0.5003095975232199, 0.5513931888544893,
             0.5996904024767803, 0.6507739938080496, 0.6981424148606812,
             0.7520123839009288, 0.8021671826625388, 0.8532507739938081,
             0.9034055727554181, 0.9386996904024769, 0.9591331269349846,
             0.9749226006191952, 0.9832817337461301, 0.9916408668730652]
cL_wsh2 = [1.1906542056074767, 1.2130841121495326, 1.2355140186915887,
           1.250467289719626, 1.263551401869159, 1.2710280373831775,
           1.2803738317757007, 1.2822429906542054, 1.2897196261682242,
           1.2897196261682242, 1.2859813084112148, 1.2859813084112148,
           1.2803738317757007, 1.2766355140186916, 1.2654205607476636,
           1.250467289719626, 1.2205607476635514, 1.1813084112149532,
           1.0990654205607477, 0.9925233644859813, 0.8934579439252337,
           0.788785046728972, 0.6953271028037384, 0.6018691588785048]
cLdist_wsh2 = np.array([yloc_wsh2, cL_wsh2]).T

cLdist_array_list = [cLdist_wsh0, cLdist_wsh2]


# %%Define funxtion to set analysis parameters

def setVSPAEROsweepinput(alpha_i, alpha_f, alpha_npts, mach=0.0, x_cg=0.0,
                         y_cg=0.0, z_cg=0.0,
                         chord_mgc=(root_chord+tip_chord)/2):
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
fig1, ax1 = plt.subplots(1, sharey=True, dpi=DPI)
for i, twist in enumerate(twist_array):
    alpha_i = alpha_max_list[i]
    alpha_f = alpha_i + 1
    alpha_npts = 1
    alpha_array = np.linspace(alpha_i, alpha_f, alpha_npts)

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
                         mach=mach, x_cg=xloc_mgc, z_cg=zloc_mgc,
                         chord_mgc=chord_mgc)

    vsp.ClearVSPModel()
    vsp.ReadVSPFile(FDIR)
    vsp.Update()

    subprocess.run(["vsp", "-script", VSPSCRIPT], shell=True, cwd=OUTPUTDIR)

    loaddist_array = np.loadtxt(
        os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.lod"), skiprows=19,
        max_rows=spanwise_tess-1)

    refgeom_array = np.loadtxt(
        os.path.join(OUTPUTDIR, FNAME[:-5] + "_DegenGeom.lod"), skiprows=3,
        max_rows=14, usecols=1)

    cL_array = loaddist_array[:, 7]
    yloc_array = loaddist_array[:, 1]


    ax1.plot(yloc_array, cL_array,
             label="VSPAERO, " + r"$\mathdefault{\phi_{G}}=$" +
             "{0}°".format(int(twist)))
    ax1.plot(cLdist_array_list[i][:, 0], cLdist_array_list[i][:, 1],
             linestyle="None", color=PALETTE[i], marker=MARKERS[1], alpha=0.5,
             label="Experimental, " +
             r"$\mathdefault{\phi_{G}}=$" + "{0}°".format(int(twist)))
    # ax1.fill_between(cLdist_array_list[i][:, 0], cLdist_array_list[i][:, 1]*(1 + prcnt_error),
    #                   cLdist_array_list[i][:, 1]*(1 - prcnt_error), alpha=0.25,
    #                   color=PALETTE[1])
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel("Normalized Span")
    ax1.set_ylabel("Lift Coefficient")

    ax1.legend()


    fig1.savefig(os.path.join(GRAPHICS_DIR, "lift_dist-wsht.pdf".format(twist)), format="pdf",
                 bbox_inches="tight")

# %% Error calculation

    cLfromyloc = interpolate.interp1d(
        cLdist_array_list[i][:, 0], cLdist_array_list[i][:, 1], fill_value="extrapolate")
    expcL4error = cLfromyloc(yloc_array)

    cLdist_error = np.mean(np.abs((cL_array - expcL4error)/expcL4error) * 100)
    print(cLdist_error)
