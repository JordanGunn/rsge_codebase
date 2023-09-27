# ------------------------------------------------------------------------------
# This file manages global variables between all LiCal modules.
# ------------------------------------------------------------------------------

class LiCalVersion:
    def __init__(self, major, minor, micro):
        self.major = major
        self.minor = minor
        self.micro = micro


# Update software version here to populate throughout LiCal files:
# (also need to update .spec file)
LICAL_VERSION = LiCalVersion(3, 4, 3)

SOFTWARE_NAME = (
    "LiCal v. "
    f"{LICAL_VERSION.major}.{LICAL_VERSION.minor}.{LICAL_VERSION.micro}"
)

# How much of the swath to sample for test points in percentage
# This is set by the user in the GUI, but uses this by default in CLI
TEST_SAMPLE_SIZE = 3

# Acceptable data quality statistic thresholds (in centimeters).
# These values need formalizing, with in-depth mathematical support.
MAX_FLAT_MEAN = 2
MAX_OV_RMSD = 6

V_ERROR_THRESH = 8
H_ERROR_THRESH = 12

V_RMSE_THRESH = 8
H_RMSE_THRESH = 12

# Sample threshold for writing reports and generating statistics
SAMPLE_NUM_THRESHOLD = 13000


class AnsiColors:
    black = u"\u001b[30m"
    red = u"\u001b[31m"
    green = u"\u001b[32m"
    yellow = u"\u001b[33m"
    blue = u"\u001b[34m"
    magenta = u"\u001b[35m"
    cyan = u"\u001b[36m"
    white = u"\u001b[37m"
    reset = u"\u001b[0m"


dashline = f"\n{'-' * 80}\n"

# About text
ABOUT_TEXT = (
    "LiCal tests inter-swath Lidar accuracy to assist in detecting systematic errors "
    "in Lidar data. It does this by making a series of surface normal magnitude "
    "measurements, and then running a number of statistical tests on the resulting "
    "residuals.\n\n"
    # COMMENTING OUT: UNZIP METHOD UPDATED TO LAZRS for v3.4.2
    # "This software uses rapidlasso GmbH's LASzip as a library "
    # "under the GNU Lesser General Public License. "
    # "The LASzip source code and further licensing information "
    # "can be found at <https://rapidlasso.com>.\n\n"
    "LiCal was developed at GeoBC by Graeme Prendergast, "
    "Brett Edwards, Jordan Godau, and Natalie Jackson, "
    "supervised by Harald Steiner.\n\n"
    "Any questions about LiCal can be directed to Harald Steiner, at "
    "Harald.Steiner@gov.bc.ca."
)

# Help text
HELP_TEXT = (
    "LiCal will run on any folder/subfolders containing Lidar swaths. "
    "More reliable results will occur in areas with less vegetation.\n\n "
    "Usage:\n\n"
    "    1. Select a directory of Raw Swaths as input, \n"
    "       or select a directory of Tiled Lidar.\n"
    "        (optionally add subdirectories)\n\n"
    "    2. Choose what percentage of the Lidar will be sampled.\n"
    "         A lower percentage means faster runtime, but\n"
    "         potentially less reliable results (default is 3%).\n\n"
    "    3. Set the relative accuracy thresholds for the project.\n"
    "         If unsure what to put here, just use the default\n"
    "         GeoBC standard (8cm vertical, 35cm horizontal).\n\n"
    "    4. Select a location to save the summary report and csv.\n\n"
    "    5. Specify a company name so that the source of the report\n"
    "         can be identified.\n\n"
    "    6. Click \"Add To Queue\".\n\n"
    "    7. Repeat steps 1-6 until all needed tests are added to the\n"
    "         queue.\n\n"
    "    8. Click \"Process Queue\".\n\n"
    "After clicking \"Process Queue\", the LiCal window will remain open, "
    "and the command line window will provide progress updates. "
    "If running LiCal on very large Lidar files, it may take up to a "
    "few minutes to decompress (if .laz files) and sort point cloud data.\n\n"
)

# Disclaimer text
DISCLAIMER_TEXT = (
    "This software is supplied as an evaluation tool for data providers "
    "to check for systematic errors in Lidar point cloud data sets. "
    "The final output report does in no way lead to the acceptance of a "
    "related Lidar data submission to the Province. GeoBC assumes no "
    "responsibility for errors or omissions in the software or "
    "documentation available.\n\n"
    "In no event shall GeoBC be liable to the user or any third parties "
    "for any special, punitive, incidental, indirect or consequential "
    "damages of any kind, or any damages whatsoever, including, without "
    "limitation, those resulting from loss of use, data or profits, "
    "whether or not GeoBC has been advised of the possibility of such "
    "damages, and on any theory of liability, arising out of or in "
    "connection with the use of this software.\n\n"
    "The use of the software downloaded through the provincial website "
    "is done at your own discretion and risk and with agreement that you "
    "will be solely responsible for any damage to your computer system "
    "or loss of data that results from such activities. No advice or "
    "information, whether oral or written, obtained from GeoBC or from "
    "the provincial website shall create any warranty for the software.\n\n"
    "By clicking OK you confirm that you have read and agree to the above "
    "disclaimer."
)


# Base64 encoding of the icon for the Province of BC
BC_LOGO_B64 = (
"""
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAD/////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////fz8/+ri3f/x7Or/8Ozp//Tw7v/x7er/8+/s//Pu7P/6+Pf/
593Y//Xy7//v6uf/8ezp/+7n4//18vD/9fLw//Xy8P/18e///f38/+jf2v/6+Pj/6eDb//Hs
6f/y7ev/8u7r//Dq5//y7er/+ff2//f08v/r49///v7+//7+/f/Tw7v/zLmv/+Tc1//g1c//
ybes/9HBuP/p4t7/zbuw/+jh3f+ohnT/7eXh/9rNxP/DraH/39TM/+LY0//Yy8P/6OHd/8ay
pv/p4d3/qYd1//Xy8P+vkID/39XO/829sv/CrJ//zbmv/9zRyf/j2tT/yLOn/8m3rP/+/f3/
/Pv7/596Zv/////////////////DraH/3c/I///////NvLD/3dLL/7KVhf//////9/Px/76m
mP//////7efj/+DVzv/l3Nf/wqyf/9fKwv+vjn3//////7ecjP/g19D/wqyf/8+8s//Wxr7/
/f39/+HX0P+oiHb/8e3q///////8+/v/o35q/////////////////9TFvP/YysL/+fj2/7id
j//k3df/pYNy///////w6+n/tJmK///////h19D/39XO/7WZiv/f0sz/8+/t/5dvWf/5+Pj/
rIx6/9fJwf+xlYX/28/I/8ezqP//////1se+/8Ovov/6+fj///////7+/v/c0Mn/zLuw/9/V
zv/Uxb3/5dzX//Pv7f/p4t7/6eHc//j39f/f0sv///////b08//l3Nb//f38//Dr6P/v6ub/
5NnT//v5+P//////3tLL//n39v/bzsf/6eLd/+zm4f/w6+f/6uPe///////w6+j/9PHv//7+
/v////////////39/f/08e//+ff2/+vj3//azMP/28/I//Xx8P/w7Or/4dXN//n5+P/k2tX/
6+bh/+LX0f/29fL/7OTg/+bf2f/7+/r/5t3Z/+rk4P/n4Nr/39bO//Lv7f/r5uH/5t3Y//f2
9f/l3db/7+nn////////////////////////////////////////////7OXg/8aypv/s5uP/
uZ6Q/+/r5/+3nI3/6ODc/7+mmf/39PL/vKSW///////azMT/2szE///////CrJ//7Ofk/9vO
x///////uJ2N//bz8f/DraD//////9bGvv/cz8j/////////////////////////////////
///////////s5eD/y7qv/+ji3v+nhnX/7+rl/62Me/+qinn/9PTw//Xx7/+9pJX//////9vN
xf/bzcX//////8KqnP/r5+T/+fj2/7OYh//Cq5//9PDu/6uKef/e0cj/waib/97Ryv//////
/////////////////////////////////////+3m4v/CrJ7/tZuL/825rv/59/X/tJiJ//z6
+v+ujn3/+ff1/7uhk///////2szE/9vNxf//////wKea/+/r6f+3no7/5+Db//j39v/y7ev/
xK2g///////Vxr3/3M/H////////////////////////////////////////////6uPe/8y7
sP/Xy8L/xK6i/+Pb1f/Nuq//287G/+be2f/u7On/yLWp/9/Vz//Qwbj/2MrC/9zQyf/Muq//
5t7a/+vl4f/i2NL/1sjA/+vm4v/Tw7r/+/z7/9jLw//l3Nj/////////////////////////
///////////////////08e//4tfR/+Pa1P/8+/v/////////////////////////////////
///////////39PP/7+nm/+ri3v/k2dP/49jS/+Tb1f/r49//7+nm//r5+P//////////////
////////////////////////////////////////////////////////////////////////
///////////6+fj/7+nl/+LX0f/UxLv/v6ea/6aDcP+PYkv/fEku/3E5G/9vNxj/dD4g/4JQ
Nv+TalL/ro99/868sf/t5uL/////////////////////////////////////////////////
5NrU/8axpP/Twrr/2MjA/9fGvv/OvLH/wquc/7GTgv+dd2L/iFlA/3U+IP9uNBX/cTkZ/3M8
Hf91PiD/dj8h/3ZAIf91PyH/dD0f/3I7HP9wNxj/dD0e/5ZtVv/d0Mn/////////////////
//////////////////////39/f+4nY3/bzYX/39NMv+DUzj/g1E2/3pGKf9wOBn/cDcY/3I6
G/90PR7/dj8h/3ZAIv92QCL/dkAi/3ZAIv92QCL/dkAi/3ZAIv92QCL/dkAi/3ZAIv92PyH/
bDER/7KVhf/7+vn/////////////////////////////////+vj3/7OWhv9vNhb/dD4g/3Q+
H/90Ph//dT8g/3ZAIv91PyD/cDcX/3I7HP92QCL/dkAi/3ZAIv92QCL/dj8h/3E5Gv91PiD/
dkAi/3ZAIv92QCL/dkAi/3ZAIv9wOBj/ro99//f18///////////////////////////////
///7+vn/tpqK/283F/92QCL/dkAi/3ZAIv92QCL/dD0f/3lEJ/+6opT/mHBb/241Ff91PiD/
dT8h/3A4GP9yOhz/pIFu/3pGKv9yOxz/dkAi/3ZAIv92QCL/dkAi/3A3GP+wk4H/+ff1////
///////////////////////////////////CqJr/cDMS/3ZAIv92QCL/dT4f/3Q9Hv+GVzz/
4NfQ//z7+v/z7+z/w66h/3tILP93QiX/s5WF/+LX0P/39PL/6OHb/512YP9wNRf/czgZ/3Y8
HP92QCL/bzQU/7yikv/+//7//////////////////////////////////////8HW3/9iZmf/
dD4i/3c/IP+HZFD/il1E/9zh5f////7////////////+/v7/5NrU/+LY0f/9/Pv/////////
////////4u7z/8O9uv+gtL3/coeQ/3Q9H/9uSDT/x8TC////////////////////////////
////////////////1+/6/1q97P9bka7/lrDB/6nV7/+b0O//zun2/+j0+v//////////////
//////////////////////////////D5/P/U6vj/kc7v/5HO8P+bzuz/cqbE/2enxP/R7/z/
///////////////////////////////////////////9/v7/ltLw/1W26P9Vt+j/Vrjo/5jT
7/+k1PD/5/X8/+j0+v/+///////////////////////////////u9/z/6fX7/6zY8f+X0u//
YL3p/z6v5P9Jseb/kNHy//n8/v//////////////////////////////////////////////
///N6vf/R7Tm/zet5P9Vuef/Zb3q/7/h9P+v2vL/zej2/9zu+f/u9/v/+Pz9//f7/v/s9vv/
6fX7/9Hp9v+n1fH/vuH0/3vE7P9Rtuj/QLDm/0Oy5v/F5/f/////////////////////////
//////////////////////////////////+Z1fD/M6vk/0Ov5f+Sy+z/esbr/4nL7f+g0+//
0en4/7Tc8//V6/j/zef3/7je9P/U6/f/otTx/5bS7/9nvun/kcvt/1e25/8xqeT/k9Pw////
//////////////////////////////////////////////////////////////b7/f+EzO7/
Wbbn/1q25v9Fseb/acDp/4jK7f+s2fL/i8zu/6nX8f+q1/H/mdHw/5jR7/+g1PD/Y73o/061
5/9FsOX/WLXm/4XM7f/x+fz/////////////////////////////////////////////////
//////////////////////P6/f+W0/D/Marj/zuv5f8+ruT/i8jr/2zA6v9kvur/esTr/4vL
7P9vwuv/Vrfn/4/K7P9Qs+b/PK7l/y2p5P+Lz+//7/n8////////////////////////////
//////////////////////////////////////////////////////f8/f+x3/P/W7zq/zir
4/9dt+b/Oa3l/0Kx5/9euOj/cL7o/0215/8yq+T/ULLm/0ev5f9Vuuj/rN3y//T7/f//////
////////////////////////////////////////////////////////////////////////
///////////////////f8vv/uOL0/3/J7P9Cseb/J6bi/zWp5P8/rOP/LKjj/0Gx5v91xuv/
tuD0/93x+v//////////////////////////////////////////////////////////////
///////////////////////////////////////////////////+////7vj9/+Lz+//Y7/r/
0uz6/9Ps+v/Y7/r/4PP7/+34/P/9/v//////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAA=
"""
)

# Base64 encoding of the GeoBC logo
GEOBC_LOGO_B64 = (
"""
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
+Di0J2ByAYsxUX8hTc/R9s2FXHXNYLJMhJE7s6bKmkSq17hV25Ur3UaIVeq4r1jmFuJVLHbh
YCjFtL+mS34s7BtlLQZt4BigYVxmeo+6rHiOXrV+nCuiTCRFGc++LNKzW1KkMWe+pT8uZkSd
c7bDOa1P38GAUb2tHnGYyByVRBZKqvkut/ligIJtrYgTJh+SPMZQ/LWvfW0CE8mOFCcjdMwv
v3FItu06Jm0dPSaJ2FTRHPCzs5g9c32gTimE2dBghXCh84B5A/ywD0D0Hn9+t/z1T16W7cpA
mMlk9o/SYtm0eoF88SM3yv13bJGNqxZIeTDxIZyGR1QZs/38aLO9s0+eemmPMRPeA/zCYXv6
B61cq5c2uo02AykljOwyMNpnKvLXH3pBduw5bqojpA5sLYTElrFqSaPc+54N8sn3XWM2tcqK
Movvy0WSLr1cDIR83W8fh4EPKiqYK4Z26mbMkVG5PveOeDAx1qIQl/cXyczbAX16HuH7SMRl
ImkMykpciyp0BH6XFC39sqQab7MddIvqrpVU3TWSqr3aFgGaw47Bb/x5Xn+dzbYSdeanTMfO
4uDAqZFOTZ8tTmD8ZKguqK8vv8qHyjRUOuF8kaE2SQ21armPiUko2DXKmpWqaNk0/Fifupju
3l0ngPr3vePqz7YnsZiI9nf5PK3/nYkkMkXki+/7Lx+Ib5IIN2GXjSi/bJDhCzpa3K6SSHsX
Omu3Q28u+CmY6NWv37JiwmrnKMQpRz7EiX+p5cG9/4066Vfb3pFvP/Kq/OjJN2yE7CSNtCxU
Zn3PTRvlH/6d203q833jiV12mbJ/ZyNMJE+1dcmz2/bbVilDw26Glk8TBsY0YpgIfc0ov1mJ
Lc/cS0oa48tAuZGgHnx8u/zwF2+YWilbRQUBf+/1a40p3nTVSnvu0nPwaflrPvi8fXzuq5jG
qz9b27tsCrFvr3C61G1weMSkPN5nmI8fDIXTAz5eTsRmIkggKhUo0Uwt+YIUqUtVr5eUSh8p
lT5SlSvULQ8c9+rHs6q1zghde4UyD2UuGKIbbtG46g/hN+lEmQBShxFvMqT82jf61yEoE/YQ
DWMLEWEm/SpBdLyozEUlGxgSEkmJ62PXDpR/rN0ikWEibygT2YeH5ZEbmijTnFXCStRZU0e+
+P4Z11wO5BYVpgBeltB3kxfkz6gVY6UZSRU2UyTBlMGahp889YZNfcX2wd5kEDL6ZNPKBXLD
luVSGpzZMp1AxVRfW2XqsjDh9GA3Z4jwm/uOy859JwLf3Gg93S1f/9FL8shzu6Rc64AEMg6a
BVLXwqY6Wa/18uqm6QRn/rMVz41XrDAVWbG+sFF1Q4XFEdAseHzmlf3SeqYr8z7PDGAiylCV
cQiLDs8HEGnUXvPuk9TaP5TU+j8RWfolkTplMKV12shDml2/BgzqHRCNMehvmA5qteIqSXe8
JHLov4icflTSMMTJgvLkZRwhUBabaabMJ6EbFxXT+vUxa4eRr71qER9cGHAxVBLMrIGRGJJ3
YVIIEzX2uWJjwTf2npATp1iFPjZaqCgvsYWDt1y9KqPC8vCjiTCi/LIRDkNezPry022zgYqI
ou49dNrWEtHvwJVvfFpsjPjQL3aYZMOaFJ4h2QDuGXjAHFGDrlrSJIv16pmMS29shDRZ+Li0
Kyq3ufVVth3PR+/cIg11laZic0x5rJ6EY5EjW638XJkes+HY2BGcT1lyAsIJoeUMcwzlAaIY
XE4EYa18qJ7YfwqppelOSS34hKRQkS37Ddve3W2xztYnEOxQHtQrqJ/7p2Uabre9t2yK8smH
JN27X4s7FL8NsLnYdOW40DKhQqNNElw0TBsT4TVhDn1VBURKP0TzzQ3CY3xnjyM+zgSTR/jj
ZNNBVFkdOirOnBCpRB0pAGM2ez+h0mLU7gnh+TrPNFhngSqLDR09wQ+DzQ4Jz4ymU209eft7
29tH5VsPv2Kzo+Yo8zMipU5ztH8wq8o5ZXL1hiXjVsRrBsHN9OJ6ld6+8OEbZEFjrb2v2aBe
MBLWyby687BNQ2YLFmbDzSxiEuYohPqI8tN2boPNUimq3SxFbKy46vcktfp/FZn/QVu1btIG
X3UQfhxIj34qqnRBzvxS0se+KemTPxEZcJKn5UM4i5sVH/AMNV1qbN1NQaDaQ1qKSi/BBcO0
SiIQKCNgMd5vCAPGd/T4UR9ngsKwDzMAs4SeeHG32aMYqQPUKhDclUsbpblxbNTqCfP5OBhI
78CgTXN97a3DtmMu24fwLBcoL2XCnpELMKNjrZ1mB/F2CKC52j/8qdPtW9fIuuWhbVWC63TD
VvXPrTZJxO8FlwsjWreO7j7Zc7BVWgJp5FIBDDoMTglkpldq8RclteafSqpipb5Qffokz7fq
+56pxxjHW75nM7jYCZhn+cmCPmXmGLPADIV6VMNjwznXq/cJ/biYmNbFhkdOnjV1xUElLBAK
PxUyF2wmT1GRvPe6NbJlrTOM5csrTjnyIU58HyZDoPVnodffYzLpTxXE92XjnnY+3d4jP/rF
G/KTp3c6aUDbFBCM7TpqqyuM8PYrw971TovsPXhK9upoOZdjJL37UKvt9AtBfPvASXOsTN+5
D5XZcdt6hJH3M6+9I8+9fsAWM1KWbAM0oLT+9xVrFspdN6238oTBYGK35vXzX+2yLU0gauEp
4uE6b169UL70sZtstlnmHVP/qJYNlyMXssNk/x7Sem3fc0xOnOq0ab1gYrow1nOmzsXIz+QF
ZqLZkxhliG9Y13CsUq9a54zkk9wzKhsWJ4hnF21m31+22I+jb2Eg5/okNdLptk1Rop3JKStP
i5cqdoxjmLNIWJTYoGks03sGmIQfH8dg9g2VKnp2m5GeUuQ3rGsaqMpYcNh8n5vWDD3JKk8u
TKWtwogT/92Sx7Rue/LSm4flWw+/alufFNr2BLCQq7y8RP7d739MfutT77HxRJQ6BMQtRy7E
iR8O48sIziffmYAvG+Vi5I4e/rs/3ybPbz9gRNXZIFwYiDo2A/au4tyMcL1ygeqapkrD0ieo
xehfiOToqJsZhUpqaHiYIEbw7RpKO9xmDBZcv6ZtPce/+b2PjlsvAlB1/c8Hn5eHntxhdh3O
2w9PEfeqM3Y5+MBtm+SPf+fDpmLy4Gl2L1GeyfR5LnBo1X///nM2WwxGSkZRDA6JGiM8Mw3/
3mduk9/4xM3mHwcX8jyRKFh8f68unBa75crQWduwMY3hfKhdCQfSpIbJkScHXBnTYCry4s9K
au3/rsyk3qUd0Vm2dxZH8h75H5Le9yfqMaL1z6HaCtqbFfusmpdN/0FSi5LzRCaL6cojUhIh
4mTgM2Gki3qDESo7nkK8ogqAH86mAeuV7eA36qiSmS4QvcnmPxPwZcRx4t2egyflqEpabLnR
2ePWDjAbCoM2o39HVN0KZ9R0EFy+IwgojipRL5z5QZC1/oQdGhmxNAYGR2w67NnufunQfE6p
hMGCO9qUzQdpSdqU2VCUCxDm//ves7bdjJtWXTTeEK1+bEHCDsvtHX227qGQa8uE6834dSgh
xd7CCYCkRf0H+rXMmrbVOaiLd+zqC1HFMXHCrsp82E79Q+/dMmHGFScP/sUPnlcJ55gRGurh
6wj8G7F6aZPccs1qm9bL+zLT74q1oZa9U+t/qKVdJa4z5gcT8cXjnUVqwB+GynqZLesW2Rby
HvnKafXMSCJvqCSyC191Y4wqA4gtq88jJJGZAGUziYide5UJmGTSp5IiGziy+t3KHgQeB/Xn
2XCHTb+1tSmlbJOjAxyqFmoPq7/daBt275R02zP6nOFLLklEyxO0GRMDbM0Lx+Oy+FD9ZwP9
uBzg+yXTPzmQUmI2ocXDkeiQQokAwnX09NuI+Gv/5WdyVgmQ38U3V3yILiPnr3z8Zvnix24y
VUeuFdRxy5ELceJHhYEgosphtM+IFNXQnPJiqxun/FF+CCIOYsIIGgJjRMaIiyaif4KLg7Y4
jU5+OE9sGeXTJjDgESW8qHj61LH/FAcmQYAhnqy1ADCjZ1/dL7/9L78tb+87IXWhU/gAadOe
SCCUM3/tx0AbENf9yPwx+J8wKh8kCpm6KkivTNuHHYI/cc/V8vtfuitj/AfYOTjb5Pf+zx/I
7ndapC5LSgG0D2X6wK2b5Av33yD33LzBRv1WTk0/lF0GPJtKn2eD7e8PHj+jzPo5+X+/86yF
z17FDkgLx+LK3/7s7fLPfvsDdjJiNsOMwqyQRCLih/2tuwdPO0nhxPf02ZB6si1MBLNTEFdG
uhwDWf5bwXoOdyZLdrruPBF9p47+lZzb/c81Hicq8lxdRLlAenRAWJMiy37TpB2p3pizLGHM
VFuFcTnkwfNCIP60qbN8uAcff91ONkRPz+wakCs+Uz0Zcb7vlg3y+Q9eLx+8fXNO42XccuRC
nPhRYbp6++XRX70t//y//NRmQHGMqht5Bo5AwR9HWLU5gySiciOOhQmQuQtuGMn6x4RjhA8z
YSEbK/s5wAtGAg4cOy0/efpN+a/ffMY2vWTFNvB1ID77Ol21YYltjZ7vpMkwiD1WwmjkC8Mz
imBH0OpHTb51ynxZYb6FMz1WzstIS2DbrqN2SBZ7fbFtfdRhZkgx1AcV0W9+8hY7IyQjiWi4
sZBj4Fk4jSjECeNVef/5b5+Wf/6nP7V652YibIcyJB+64wr56qdvlZu1r9jYsRAuBSYCbLfd
00+YasvWg4z2aTnH27ccgvcY43epSi81myW15p+41fV4h9IlGJtKUsn0sb+Vc3v+hU0XVhmQ
J6HKjwfTh80YzwFdiz8vqfnaJgkTiY3pymPamchjz+2S3/nX3zNi4Ee/ueIzUwdisnzxXPnE
vdfIP/7y3baK3RcpHC9uOXIhTvyoMEgGz772jvzb//GY7HrnpI2a2UpkuE9fYCVsVkEllspZ
9GNSUV3f4WxVTBj4+/qFYaH1D49GRzVdzUeHsFKtTIvtYTarlHbbtavl0++/1lR/4KmX98rf
/PgleeKFPcGUWEd8vQ2CTS3vuH6tfOTOKx0h07RRJUSXbHpB9SHtXItV6sDATxnq2J5diX+4
edje/c++/ay8fbDVDrUKS6O+rbwk8k++8j75+5+7XdOqGLePVhSm2ue5gL3vn/3pT0y9h4rO
DybCID3ekS3rFlu7f+mjN8Ta0me2MhGDPqMX/HNbSKhlTL/z783QnrFdZMen4DAT7lnFziyv
pb+mHwj7m2UR+6CS6ZYHgzPWTyhxYvquhstZLh1YsLYEddniL0jR6j9waVAXnueIN6NtFeDd
lMe0zc4ChDt2qsN2W4UYMILDL1d878uWGBCY979nk83ayRUnVzpxESd+dhgYIaoXVnqzwI3j
Uuc310qTSgaNTbXS3FwnDXpfV1cpNTUVNjqGuHFAEiNwHBMMIIzO4Rf+ra6kxKblovZgrQ1t
sUAliPWrFsi1G5faSvM7blgn7926RlYsbswwixe3H7R9sk6d7bGRujf2Ir0UF6eM8XC2xsfv
vkoWz3OHM9n1ArhF5urswKsF2k7stMtWIs6eY8XM4NFf7ZIfP/WGTRGG4ISlFA/HGIvkA7du
tu1O8jHqMM43TPgj4gAuZrdhF2JrFmcXiY6r0exdeM81q2zbfNIBOfPK2EQu7OysMHLGV3+e
UQMkBjsad/CUSNsv9GXr1WcBM8+Oz0/qADM4N6hlXa5uibOrZM+8sqj6p/+QW/k+0mn7eVn8
nPVSfx6xhxezv+bda+laPXLGcZixtgrh3ZLH2Fs6TSguUqKpRM4ImvtuCgJjctvZXvs4ZyMg
gp++7xr5R79+j/zJ794vf/bPPid/9a9/Tf7ijx+Q/+effFL+8Cv3ypfuv0Hed/N6Wbt8njKE
IpsWCmGPhaCPkMzYUvzKdUvkf/m1u+Q//eGnLP1/+tX3qwRyjWxau9DsAB4c78q5FqhaoroZ
IoYtInY5LgJgDiw4ZZIC97leWPxZOGkLFwO/Cw3afsm8BmPiEabEDGCCvcpkmHHG4sjLEiVV
2ikMZiAhhXpEGYYSd85zT3M0r83sykbQ70g1KdaKwGRi9DTMebRHmQ5npvRctHfj3YxpZyKV
FaWysLHGjLkQhXyAMBjR0HDM/nlz3wlp72DxkIMfvV0MkLd3SA8cPAQzwcaAeoIjUq+7YrmN
iu+7dZN84t6r5Qv33yh/7zO3yu8+cIcylA0yv7HWdOeF9lIKj1Kxd3z1M7fYTrtsTMl6A0bz
5I+UhmTkAeHloCkv8WXDtGzWvoGHvynUrHHaPUaYQiFQUTFZoad3IGPzmFgLlw51QVIrUQmL
+wuFcLuyTTznzVfNKc/bp6i52M6HzRu5gsy7fikj3KFs2siuwGXztN9GcvS1q6/Vnfve/U7K
8kzE3iF14XeJg66qN5jBPHe6AcLtOXRa0p3b9arMJIO8sRNME6aFidjHH3RorY7W1uloHJUM
M5vioLS0xGa0vPzmQdt+2+NifnT+o88ug2csHqijFiiRv2LdYmMoD6hE8oe/oZLJR2+UrZuX
mnqK0Wh2vDDwh/BUatjbr+e42qszuxoTJSou0gdTqjG627OIpoJID4+iIvJxg0AFmjW6lOMR
J0yh3mNiBTPPMETn7Wuqp89hIMx+Qxq5GMCeg/2OPmUmXRQoGVXBLsL29RzYdfnAOsLdsntu
453uzBKM7XkRkBm2jDdJZMT9Jq1sI50yp1T9DXrV99+HywOiYpNJD7VLuv05bfiT7gGwucQJ
ZhrTLokwBZbZQOjAmRoZh9gwumZUvXP/SWlt6w58FXEiz0KUKGO584Z18tn7tppRfHBo2Ihg
LkKJJMEoe+G8emO+cYDdg9H7kDGo8d+hB+s3cLMV1Bvbgu2lFaOvsRFYO9oP87qgQI3FIVh+
d+RIBIWziwaZ+T20LhKKayRdc4US+8aA2MfoQCYPoHqKVGcF0PTStVfpR1SjYTGsxwD2Fbak
79mt17AkkuBCIJKJ+JGv/1DCv6OcDwNqa+bYCHyFjtiwjUQZSbOBEZiRG/s/cchPBho1O4+p
ujjx44YBUc9wHg11VXLtpqVmXA6fhREFpaV2kt7aZU3SPFc/ngAuvfF5+ivqFH9eOu2UbYSF
jEGgGQn7YvkyFnJxwsYJk88B1J2DgyNWByszDCLrffF+xkCQQLKeR6XtXaHnuLhhAPtoza2t
MPUmpcguqwE/dc7wPzY12SM77fAzB0vZHI/8Y3/vFH7ejUdU2nFdnPg+jIHFh9VrTXJwZXE7
NUc66kIYmM05dYGEoY9MWHBhAhTPkVTVSpHqDfpRLNKkgw1DSUMDj0vX4pF2iTKPPrHjdTlP
XkF6Lu3c9ZiqixM/Tph8Lk78OGHyuULx4yKSiYx9uO5FDf+Ocj4MwJi7emmzrFs+XxY115mB
vZBai7hMmUS1wQZ2IKoS4Twn6+LEjxMmnwPhDoDoMFOpoabSiH6ujhkZHbXR7YpFjdJYNyaJ
5MoDMIqH+KIS4j6ctoY0As1EBZw+DZ44RKUbdtMVJp8DlHnknDtPhvKG287D+7GNBtuvZCMq
be8KPcfFDQPKSorcwk0IW1abZ4BXpsxp0VKPsw3mS9/BEjDHI//Y30Myx8KMR1TacV2c+D4M
ORtTR+VUxpG7pRTMykawCQ5/YvGDayCJ8Muc+jPri/bitxntG24U4eAspAxlOixGZN3IuHRx
QZ6SHlSxr12ZSCcp6G+XVsZpoOx6TNXFiR8nTD4XJ36cMPlcofhxMe3qLEAB7rpxnXz8nquM
OKK7zwekFWdk7bdplGc4XjeP4fJSAUb1uXXVUl3l1r6EaMk48IywqLKyNyaMAsmQlm0x4tsp
1Oe+/8909JrTV8J5zDJQD/hCrnbJhrWhEW9+OL8LiSLtI1vjYjaZ/AWgrIDp4X7q9eUC2/vK
o6ROpLRBb6hjnE4hTEQ4CFfmVhlU012San6f3jsmkh+aN3aZkXZJD5yQ9JDbJDKD2fn6XzaY
1rfbfzgAVc4Hbt0kS+fX2zoJP9KMAkyH59hQdh84Ka+8edj2kboUEebiXGuUgbACO0fVDTzD
sM5CSw72KghLS9uTf0HC4e/E589+W9iYvF4+XLbZAEpiGy0WKpM+ppoMNJhQEDTARYAbheeD
MTrfJ1ovpNHLD6FWYM0KjEQJf7x+oa9z9DfvAe3HfVmTzf5Kc+ytbQ+fY1BpyfFHY2Fz6d4p
0rVdfzpph7SC7rh8EbRZVDXtXZzhBpixIRI64RVLGuWqDYtlQVNNXpUWFYWQILW8seeEbTPS
2T1gz2Yb4ZsMKDb6c79FRj4wDnPHyMbokqA5wm2T/ZrQpv19A7aJIivsZyPoc7//WL4e5hn1
MfVdoPq6GGAngSGVqlEfZjohB+gX6sVK/csarBUxIq/tEatfNBzSRQ6YEkrToXVTxdhdNquk
owwlnzGetx8mxlqUrtcl3f6MdpZTi9tHGHwjCWYG08pE+HD42I37KVipe/8dV8qV6xab3j/8
LBv0M6PxljOd8vKbh+TJF3dLy+lAv3mJAsbAYr+xtR3RdadJqD/h4vIQ2pr2yjCdUNKesZAY
0gjnc7AtikeOLrjgoOyo72C0hQDjwEg9MBCa1nyBwUw3JiuYCjEPXaJs7GPG++/3M5s++Iyp
/0XqSP9+GfQ+7lRaYzgsJswnnWHjCNKzacTvtVX57NlltZ3Q74TlSwsGIv1HRc6+KOnTT0p6
oDV4qpgtL/0MIK3tZSdTYjfsPSzpzjet7rZBJW2Jm8H6TysTARTavwSoZ5jqunH1woIqC+IQ
BvvJO8fOyA+f3C6v7DwcPHXPLzVQZBhD4dX77mGxRohbTwgwEg4uO4onsKxhQRL5xUt75UjL
2PqbAoW5YKBtmALNZIwJlYgAxJtt6NmS/mJII6gFyd/OiM9TXiQVNpxkoWhluWMi+QZQUwNp
XZx+HFcPJAQ/xTdnkwThM6qvYNBAOjnaBF87zKrxViUka/WFL3DiIf2BG+mTdPduSbc8JDbl
NwCE9nIFNUunlcmyFY1KYey9lm79iVvc6TGD9Z92JhIGRKK2eo7tIFta6uwCThWQG4j/fKy/
ev2A7NhzwkaflzQm03kaNFZoTROGWxIwEsZhUR8X6jHOtuAUwtMhSWS2gKndbA+PGjMOU6CW
1IfJAhdj4kWGiYy6WUK5QF1qq8ptdmIcKWtKMAIc3F9M2LRd1nNQmAJvrxnhGzVYTLKDmqxy
lQgnKxIP5FVrKZB0UGV1vqJSydgg9LIHde5V5nn655I+8ueS3v+vRNqeCh7OLIr8CCnspgdj
6bCT7Fc/fYusXMLGa/okTz6MxFkNzHTf198+Ik+9stc2cwTTW74LA/usCnxbkwXJwSBY/IZz
beqehYEENDA4JIdPtNmxxWzBAfGljV1bBgEvEigfI/bG+iq7Il1l9y9lDbsjLe12jO7wsGMi
F/KdYKPQA0fPZDZfjAJFYfEkU7uv37JcanQQBXz5pweaCYS74KylmQH1oMWt1VmXMXRGf9Af
0fWz6dlMz61aJ1K7RYMFdiLaI0eb2NbwdlMsqXnvl9TSL9m6lDSMhbxy9jlS/7DIYKukO183
qYSZW+RyId+VCwHrB+rEj8EWSZ9U6avzNe2TNlf/c86uPFX4tvLtFuWADmjHf6S46UCQvoFd
aP/B526znWjZIsQVIFenUgZnkOYwqB89+Ya0nOlyT4LyRceb3Zju0iKJoG9n3YIR38A/DNoR
htzdO2iz3nbubzEC557ZZ2X3FwO+/yjGouZ6U/2w8zEr8aPArFpsQBDxN/ccVwn1whDQ8HvG
wIYz6Hv7lImoBJgNH5br0oVz9b1fYefPTCtoMIgoBKLgdiMzi/QoxFoJFuszopgI7WFtEjxj
1+G66/Q23mQDYuJSdVdJatmXRJrvFpmzRJNkJwyfdhYyRdA8O5Sgtv5M0kNaRsV00reLCq33
OPp3blSZ5VsqhTwq6YHjbmYb29Fw9YhqqwLwbeXbLcqBGVVnhTGvsUa++JEb5O6b1tkOt35E
nAvMr+dMkhd3HJSTpx0TSTAeTB3m4C9rxjwvCXT5aMtZ2acEcDTYBmXcS3iRwey9tcuazYaT
S03FuwLjPHqyQ/aoVFVILToTYGdeJn5wJDAMLQr0BVPa582tNsbIfXxQ9zj10jDnVDq38zYu
ElQSSkGwRju10oFfTmh5CVO5XKR6jd5PYcYaBHHh55WhbNU82Y+MNCMytuZTf+wuPTtNvcN+
XbPpfZ9O8F2kO16RdNuzKoF0a7/o4IqdkCtDKsAZxowxEaucdpzvPIzsWzcvk+s2LzdRn/UB
bHUCwsyEWyMYwXMMwj94fLs89/o7zqBpYRwXvFxfjHwI15kjcxfrKB6Gm21T8G2k/+375Wxw
bCPdfeOnTs+GNmRnXKRVCC47F+QDNokTpzrtvHvg6zFTCKfNkc9R6ixaEAdjoy/YvXl+U61t
1Di5smkqBftD02PUP9KjxPT81BXnhRElWN1vqiRyRosU2H2i6orKjSNs2WcL2waI0yYaxs4u
8e1RXGnnp0jNZuXSTPlV2mK2mIlw74RK56O9ksZOcPxbIm3PaHhm9bnn8dp6NsIqYHWg9Gne
A6Y0cy69qa9GJcVZ81UbJcXhZR5W55nBjEoirjPHCq+/7LyNW65ZZdubw0hALkLGrB2mBn/n
kVflb3/6is3aYnqnhzUkL9Ml8DLMRBeiBtqwcr4RX9bhRLUFbQRDPn6qQ3bsOS57DrVmticH
M9WGPs046bJj8bWbl9qUWDaijIrn3yVeGWxkzNzDPjKT8CXwZWk902XSMQthx0kiPFfHQsjy
smJZrUyRYwMmB5eGXfNCP1mMy6zKViJ5YaF19v2CLQR10WCrekdIFhrOagMTKV8kqaZ7JFWx
2L4DXJz3QjvcHCF9vFTVatsOJVXerI9KLJ1cabHOxE6CPPFtSbd8T6Rnr/4O1o+QWvDua2mc
16yGltHalFYIQN369rtJBL17Ak99P6i3MduF5jPTtZtRJhKFazYskd/9wh3y2Q9cJxtWLbTZ
V7lmYPEO0cd9A8PyzKv75N//5ROyW4ngZQvek+A2Djauni+3bl0tJaXFttrfE9pcQJ//J3/+
qDz8zK7AZ3aA0w5XLGqyCRjrVsyz2U/0e1RdYJjtXX3y/cdel+27jwa+vCcz96lgR9p98KQO
YtryqtGw5yB98I6vWhLSR8cFBLfQ7CP7KDTcUIsS8vC07dz9Pm0IZzF40i3qG9A+KMqx7sP6
T99JTjSc9wEdFY6dwjg5hNp87i1StOoPdAT1eTf119R6udqMttK4GNrP/ELSh/5U2611xonq
jCL8nvcfkhTMsfcd99s+GiXpnBzZcL1I5VTbe3K4IEzEf+BcWReASusz910r7791o0kkTFPN
3u0UQETww/fAsXYlfjvlFy/tkZNtXZmwnnBmx50tsPLHLBoqqclUo7qSs9cXqXTXLLXB+S3k
Fya+vn3Y76mNNSMv7pGfPv2mbHvrSEaqm6k29OnSt0zNRQIaHnbHA/j8fJ7Nc6vl3vdskC1r
F5ldJPwsDNRFff1DJomgovMgvemE5R3kT/m37z6u+Z3O1GnMWRAD/VddUS7XboKJjOmjo+ox
AYTBUA6DyAs+WSWabDQ4ElqMO73VnwhfB19hJBAdBac5xlbcrsbjcc7FYVpv5SpJ1VyhAktV
hoBPpr9sry5Ni3Z0a0duk9Siz4g03SmpsvmaFhti+nN1QunSP1y0zdIcu3v6MUmfekQZ33EN
y4wxXw51vn6zElo29z/TbulzgyqBbNP6PGbn0TuVoobAdoS0VrHM6m5tNsN1u6CSSKYBtFJX
cP737Zvl+iuW29kjbk8kHrpLGKi9cEgkT7ywRx7RkTSbNc520HfnIOzUzVU9ErQL1WYmVZz1
EmFwUNJt1642tZYnvlEge2YUMVLetuuI/O3PXpGWGZywECYSp9p7TJW2+0CrnDrbnSljuEmY
jXft5iWydkWzMYpc7UWySANIXmyN06/vxEwZ2X0RmAiy/8gpOd7aYcb9UNWsj+2qjn3PGuur
bRdr3unJQVMIz7jKUX+D5al/2CtqWPvQZkbNILSSQTXtXgZPK+Hyhz/lICGEg7CpFAJBS3u7
yRRhapyg4SmNnS/fdI9+ANeJlNarZz4Jjrhl2l59kj72N5I+8R1ttzaNM9ZumfrNUoyrP7aw
zh0qCb4s6V5ljvzW9mWXY7M7VW+ycA7EcfFmCsV/pAjuM8hFiKYLnsDUVJbbeRtV5aXSMzBo
OmdGfZx0SIMRzjuHlI1oT5zqkAM6KmQh45L57CDq0rRXfZa8DZSHszxe2HFQ3j54Uto6+oSp
uJmqhMB2GnPrKmTLuoVmZIYQgUL9QB4QXCYqcLzw20qkoacQVey+4bwsb70SB50+doXu3gGT
DIkPxtr5/OHTalWp8ae/3Cl/9dAL8vTLe5Toj2g9F9tMLArow2FjqCgvl0Mn2mXXOy02qQIj
O4wvXC5/z1kqSxa4qcFNDVUZW8p0wfIJ8uLI5gef2G77utFXSHX63x4TDgmQNr3jhrV2ouV1
m5fZRJK4sLx0ZJnuelOka4fbusMW5Ln8xwM/3KikUOfUbNTRfo0GZzHvzLz8lM+3u5Xz5IMi
J3/oRsDGLIKyEoafrJ62GUIrVGL4nKTmf9CpWHwa51nOTDqltZKas0BfnlJJIZUhHSljcG1h
Acecb8uRbkmZFHVI6W6FyJxF+lgJsIZx7Ue48yvfTMD6QK+2S7FKVHLi+/piPuukUeoXFJmd
j2XBR7RdtF5F2KqmXhffzpn2zoHir33taxOYiBU4cNm/o1ycMN75sICFciuXuIOYICJdvf02
82XMeD7WAH4hGsTPpnkeOmUEplEJCMfK2qI7/oXyAdn55nNxwuRzYfC7W5nIky/tlV0HTlq5
NdSEcIBZZzDENXYOyzxZ0FQXPJlYnrAf7YE9gcV6TEDgUC+YCadE5loMRzwINOeMHG45a6oh
2o/dhv029D597zyy/XI9M3/tumOtZ+Wx53fLtx9+TX7+q11ypKVDli1skLtvWi/h3W1tZKn/
ABIGbXVM+xjbBxIo9fR58UbwrXuCyfO1K+bb+eeZvBXhaz4XFcb7AQY1MOcHH99uCzZZZe/g
rkh/2GmWKUN74MM3yGc/eJ3UBWXxZQTh9DMOf/dQE9LR5NmXJN29XVJDJ90zJc488kHMZb6J
EUmVz9eR51IlGIuNIAZBNVxEXgXcuHjBvf7JPLNcVfpIQ7hOfNMdRRv0m4unwf3InijK3FLz
PqRM5FOSql5tYUjDZlwF6UY5ix7hn3EugEuLGVs2lZWBpDIPVGvnhpyqh/K4oMFV45I3THCg
xRmiVXohDduOhfbz7R3kk3H8DjmQ7Zft4oTJ54IEzPnfvE/ptqdVmvqGiF5l8JiWv0zLSDht
EZjpgo85+xP3Vp/x6YYdiPL3Lvz+5gLhZmyxYVxQ0CvXL7azyb/yqVvtrPIBJSQTVTPung8W
1Qd7bDH19z/9zVM2cg3P2potQEXX0dUrfcpMtGW1bYMHWWBkizEZaaW3P349wn0F8/nw7ZtV
oqmy7TmiYC+hOmxQtCZSwncf2Sb/9D/8RF5+84gLNE1obe+SZ17dL3/xg+flmdf226I7Trzk
6OTKrFE6beOxafUCO2OedUVIIlHvMdVmMgGLUZkkcPC4W0w2Ezh5plt27Dsup8/2ZKaYh8F7
hz0HG99tW1ebdI3Ka/JQAjyi9eCYV2uPAmlou6SHTisx3G/SwUzCuoANVM88I7LvX0maWVlR
5fNMpLhaUnPvEFn+206dBejIiL48X6jMLamGmyS15MsiS78kUrVK2wNVN5lFZMhMMqSk9IhK
VN+X9MH/LHJGGSOr7mcx0qz/6D2g0seLOth4wfU5s7Csitru1KukTlJIZ7arcg414yTg6UuY
N2Q7EKnOyoYPnA9xwgAfDmIWLgi6fT5G9s5iFI1k0qOj5L6BQbtHEgE+PLYD1EXtnX021RO9
O2A0zXG0Pm2fD/DXfIgTJh98voADtr7zyGuyD4Os1gHfqPQpI+oYVmxfsWaRrF+pI0wDaQW3
Ifg0wnVj9TqSGQZn1lC4g5PG58e9d8SFcSG1sFU86y/YGQDizwp3RtzVShDD8cLwv7OfYWdh
1tQPn9ghP3xyh9lCUPesUSb3mfdfK/fdstHsBcShDB4+jTLtf6Qi1HQwQxhdeAGizw83ODQq
g8F+VkRnWi37cPl3Bfh088GH8eXhNypBpLVHnn1LvvvoNjl8vN1maSH5uefuaGLaHMb46x+/
WbasXWzPge8bn7a/hmGbAhKGHzCPlu+LdL2hg0oGAe6ZR+Y2CG8/NRxjcjumlhlQPFNneVvY
zJ9JIVNmdaYi7n3HbejX8qBttQ6RtlGuBSI/Za7Yc4pUksWIjvpq/kclVbNen4+FI7WodshG
3jA8C+pnu9f6sKX1ksKonNIROP3IGpJRLSczsyCohPPOoO/UaK9KL90200yGTmmCw/q4ROlx
7bjw4ffC47zrkQO+74hrV2XM6d69ToXV+mNlIiqBmCFdn/q2pf2RqJBIm+/R92GDxafUhUow
HfW44EzEIxzef3Dsn7S4uU7m6yiU0SofMlIJI0CMzh6EdQZObCT9smP3MTl6qsNWFDN6pfkh
guFt2HOVz+ftkStcLoTjh+OiVnph+0H5ydNvKjPpdDYARb70GdVes3GpXLtpmf0maL4XOOwH
0Z1TXmbb57d19kh3z6C1n0d2vvyG2CKVEG7f4VPy9jsn5cQpZSTKTGAkEE0IOeovrtgDUO9g
jxjmbI3gWU/fgJzRkfq+I6eszg8/u1N+9Is35NU3Dxuz36jSxfves0E++/6tsn6VWwBF/mEX
rid9zxRZ+o7FpszqCq/NIAzgOWo8JBKYYVN9lTGosFrOI7ufw/D+XP09ux//SiUoGMiTL+4x
RkhbeRAOFeqGVfOVMW6S++/YErKDTMwr+7f/wHFmGFXmIdga+t7RsIGqLxQnK7p6aFnO9Ulq
VAdPJcqUGZWqBAAhh8C7CPkJybhnGt7X33oCoz2j8643Jd3+S5Hjfyvpzlc0PDtNkL5rC1NF
QnhLdRRcvUlSTXeLLPqMpOqu1iBu1laubyQXCobhuToLpWlbPSCoZY06CtH3q2yu/ta8UW2x
LsSM7loGwhsc8U1pW9nzvn02XdbqC/NBooIhFrG7tBs0+HaxNHzegPeW8kQgfz00nm2hr+UP
pWdx1Nn3MNwu0vO2pE89Kmll4HLmCWV4x7Xc5RqeGPQB6WiZWTdTf4ObuVaxxKWVKXBuFGxr
RaEwF42JZMPHL9cPE0Pv1k1LZemCuUrgxBYZnm3rNhVGdj5ILaU6eh1UInP4eJsRMaZjstPr
mmXzbFRbCOE0p1KPqDgQnv/54PNy4FibEV5vo8iVPv0NQb756pVy01XByt4Q4pQRaYa1I7x/
294+attzuHfcfQS5wCOYMqN6pCemsiLRPPnCbnlu2wEl0i0mEXA2SZtKfkh/bco0WDnOrCWm
XX/9oZfk+49tl6de3qvMqNVmz3GcLPned+sm+d0H7pBli+ZaGV2e0eXx/k6iLLWNJg9o/x9T
6aqsFD3vxLi0HWWiPBi1WS0ehUJ5hrHnYKv8x288JS/tOGQDmHC+MFcGBRj2f/MT75EHPny9
1NoGkj6dielF5ZHx4SClE992jATDL6oJEIoTEV2h7ctIu/vtYHSqxJwFfRiMQ4iMGsA/mxBG
00wf/nNlHt9wBlxG69gQLKQPrR/niI7msUk0v19SS35NUos+4YgYhG5c+d19VDtkI06YbGTi
lFRJqlKlsvrrtAzKCLB/IGUgdcAUKLv9D8IbQ9T2RgoZ1LCdO7Qftml99b5ytdZNJRwX0uDv
w36aeXAzHoXrETzXcBNC6uAg3abM+5D2wZnHtR5HrYxK8TTsWDx7+zVsqmqNyOLPSar2Kq1O
jXsOChRhOvpj1jARD0aXGF2rKstNPcHoEn16Sv0hiuxKiz2EhV3k6FVdSCCoH1BrnVICxxXC
0tc/bCNZPno/Qg0jXO6p1CE7Tk/foLz61lH57s9fs3M8KLMrpyOoucCIvV8ZYXNDjRnW2SKd
vbGIkx0v/Ds8godRMdvKb/p3Shkv+4754GNEbgzhtOzQJR3Rox5CsjihEhRM5YRKN0gELFZ8
c98JZdLHbAuVV3Ye0boetkOvtu06KoeOt0tre7d0aT/QR6jDrlXJirP2OVcmzECyJQPus/1R
cc7V/mfDQ9a4UC4YsoUN4gBaANXmWZX+1NcGDhi3sZ95+LDZyPZHdcYamh888bo89tzbclrf
Iz/lmLxxpAuzeuDD18kHb99sMwR922b6w/5MrKeH+ShRTo90Sbr1x26kqSNPM07rCJ64YYz7
yQ91eJkqiemqtpsuGyGiVlJiSTqodmyGTjRcfA3H6JtReK+OyFl7cFpHvGxceOYX6rfbyuUI
mNYNVRvhuWfaLOorlT5Siz4p0nirSQMQa+ocfjc9cvVDGHHCZODbwW55h5TIFiu9YNpvWbOT
SkocI0gjtSH1MY06RfsQHqlE/2EjYQsR2hKmM3RaUtic2LyRnQGKlSki7ZGP/Q2Qo6yF66DP
CRKUH1hrwfQ4VOvUz7QPfirpjpeMgadU2lBKZ+W1PHHWvloP/OuuF1mqTJyJFj7vGKLIdPTH
rJJEcP6j44q6YMXiRtm4aoEShTmmsoDJmOpGP2TCeZUN9zxDJ868flQyELa3dUTJVFZLV/9B
5CFwjCbRaaOm4MhVnkPI9b92pv0ZB/MnjOYHoTGVjuZDOswoY+pxv17J8+s/etGMyieViMM8
cMQFvm7ZwJ8WdLaTlCxfyNRVZzvIRtjP4gVpev/GuiqbKgwDgQE4Qzp1m5ivRsqkASEkLM7a
WYk+zBqVIXYWNj7ctb9F3th7whwMhRE7xmfaskhfcJg1NilmS61fMV8ZyNVyx3VrM+smwuX0
1zDw8+Wkn+fNrbGdigFbsduCyqDPfXVoXxqP/mDWHoMHtlDxKk/KRr8R3rWDY9qkhVoO2wp9
h/R6SKXZbz/yms3GIj8Spi1Ip6ys2CYu0LafUMb41U/fakzfw9fN6oULftseTzpity03sH2M
KFGG6KNCYetuFsCdfdnioALKVCwD9c9+IQHhuRRr+5A26Q0ccwxB82QmklNLwWTOar7qYAgw
GyOWGo6V5wNHTBqS049Lmqm7uLPPW5oQZZiRzfZBumAWEwbcsnlKsJZJqvlekYUfl1TjLerv
FhMa7dK7TFuEkP07CnHCjEMon/D7JWUNkqq5UiWTFa78SCPK+IzJ4Sw8RFiT4J+prvDXCtBm
HdonPW9JWtvLVHaabnq027UpfYqxG6Zq6jJNJ9Nv2X3FbxxhNCzO4mv/YEtirY8xrDM2+y19
9OvaBw+5PrF2pP3dYCA7ZVNfcuZK073aF/dZOCs/AWO043T0R0obfUK5whjXKTkQJ0w+hOP7
+7AfUgbTPTlYiemfjIqZdsm0UUbCAMIHAcuko/8gIkgfELSGugqpqZxjUg4jSZjSonn1dnDQ
wuZaWzkPQUACqppTalIA6hgPyoPNokelmi5lGIxQsT+wJxWEB1vCoEodELCjrWft9D3UQxNm
6lA3ZUIQZ2w9jP75Xab5LWisldXLmuwcCmZaXbV+ialJwsjV1tn+lPXIiXb51bb98ugLu+X5
1w+aSgjpYJxEonEmpubS8+CW9rQXk9/qMn2ER5AAC/9If+Oq+WYjQI01T+uENMmAAPhy5qoH
8Hn75zB+BgVMoGC7k58+85a1PeGypUsYSkNtpfZrrdugUqUEiP76FfNkpQ5IeBcoCwyHvjqm
/WdnlBw4aapHpNnjpzpNEqNvsLkAinLzVSvlI3deKZvXLLTFnbwz4TpMqBP10N9pRpbHv+sI
uS0oVALCyJ5ZRIx+OfvBtjBhVDwRtLKmEvyKgEZyTaZ/mPaKOgPHyJmZSIxeTX+uAX0GEE8j
aBBBLQsj9JFu/QmRxI6gTEgT5cQ8i1RS684DqbtKRAmzVK1R3lKnhLpJpHSu5Wf9SmhflnBb
KPL1uUecMPkQjm/FACNaH5PWTmu1lGD37FHm/arblJEtQ5gmi0rL1Ig+LrG1jYr0+8Peg8qO
+nLCIkS9VNuXKdbYYDBos9khv5GAUtrmqBSL3TtvSRnjoRxIjG2S7lO61X9QP9QTjpkj7fBu
KMOyEwrtN1OVYQpjsL3IfH9hTK9SSXD5VyW14OOa/0INr++Qexn0/vzbOk6YSCYS4XXREFUB
VC588M++tl9eeuOAzSqCsaDCgjgw6iSWjTYh2EoMuJIWKhVG2NU6umU2mDkdtcJAIDoYp/0W
64SFCdAewzpqhUmwat7PCjvd0W0qI3Txp9t7TXVleQcj+nESiDruqA5qJ4gti+Tmad5NOtqe
r47ROuqbhc01NopnIR1bm4DJ9Em4zdh59rnXD8gjynCZaktZIfZ+80vCOufuo/KxkEGa/rmT
2nD46bel6cEsrl6/SO68cb2pebBJeUym/GGE6wKe17o8qnV5Y99xeWv/SZO0suGZM/YU2pQ1
HDAQbG2o+xhEwBxgGKjfYEjvHGUg0GG2NQYP1vdaJ65sVc8O1DDFu25Yr4zJLc70iKwb5VZ/
a9Pj35Rzu/+FG23adFwIOMRAr8CMuIVtd4VBZzDKVSJD+u6NG++4WDieBc6C6QNGuxBIpA8j
nnP1p9a1vNltpVGzyTGS6vVGMC2pEKbaxzMFK1/W+2MlZLFh105j7tK5XYm2EnLUSBB43yYB
bHaU9RXtqaCvYMoQcJgnTJStV+za6JgLaj76k7Awb+sTBg+OUVs+LBpEamT1/4j+Znt7v7W/
5aF9YIw/KAvV0FvXH4tcvhVLbWv91MKPqVQY2FG1D8ZKf37w9CD7G8zGrJNEouCLmB0Gfz78
V986Yovant9+QDq6+4xIovJATeXVGMT16fgrsDv/x4cZezwRQRHcRf+6/4Yw0wCuuNgqHFOB
uXjbzLJFDbJ141K5YfNyuVYJFEbnKPj0fN35Xaito8JgaP/RL3bYIV9s3wFgrOHqhvMK1yMM
n65dgzAwZWYm3b51tXzs7ivlrpvW25HIHlHlmUw9ssM6u9Nh+eZPX5GHVSoxpuFVVkEYD+Ka
n/6J+rxQwbn0x9eNPmOGH7sH3LhlhfyDz99ujMSHyVW2cQiYBIvDzu39YyMeGkMzgDh4WMbB
PZh4b2shTPc9sfzmZ3VEWgnys78TMaGUGQmFe9RWwW+upU2SrtkiqVp17Ahbv1Vp48R3VLPW
dO2PYkIO45C3rQLECZMPE+O71rByhvzNd2RQ0j277BhZzuNIdet9GhWTZ/T6fWS3JglZPZ0/
dR8LEQ47FmYiXDm8DsBCTaizf6p9YTayUgtne5A13inphpvdfZlbmJypt6uo+RXCdPXHJcJE
7G9kGPTaqLpOmmrJGYKZSeTVTUgKnb0Dptdv7+gzddjQIKoETVQJBZ0V9Jalb81hvyfmFRTE
Xbn1v5V5lJYVS8WccjPqojLhWFQM3EgSSBzN6mrVHx3/PJV6CIPU0VhbKQ0qAfn1Bdnw3ePr
PtX+QHo7HBwty3TeA0fOyMHjZ0ydg1TVdrZXhmkXbZOU1gf4JKy6/NG2xrO2tsJUgEwAQPpA
amKtxOqlTbJ0YYNJduH8o8ozmXpEhaUfUWm+ufe42WtQSdHfbNXOO8AUZVusGJRZU7P/DsE9
6dqvtJRVVQQSabUtdFyhTB01GHViLyy2d/frZkC+smWgz8g7feYpOXfsr5Vo9Wh+GjYz2odg
QyBCqhQ/AiVNSzdwpGXlhlE4Ape5mlqK3zpaPjeiQVHBEZYr/oA0se2E8mQ0beqZMv1ZrYyj
1tRWNlWYES+HGpU1OD82PsxVT2vMXM/GMJk+nyqi49MW6pflTalN1TWkksmAusHjTkpRqSSN
ihHJERsSNgu7ntVvoF8jBm1vTNcnmp0nvy2HAP6esoTv9VJMX6D+0v4ood1DbY40WK4SPa5E
/Zn5NkedST21mVwz9SbtmO03Xf1xSTAREA7jixwVB1sAq4uxn6C6aVUmAsHBRsEMH5gJBnqk
FcJit7D1D0pwRs85VRjO1GAwGgX5uJGpM+qzKBCJgoVxrEXB8FtdWWYSRo0SI+wvtXplKxPU
J46JVCsTmaPXGtuobyLIqwBRUkymrXw7gXAcVEDGSI4qE2k9awZlmC6zm1DnoOqhPZDkKJOz
N7EOpdTUgA11VbJ4Xp3te0Z9WByJnSCMXHl7TKYeYWT7wRyPKBM5erLdpFLUmix47OoesAO4
2HqG9SxMhPAqOOJ7GxpqS7ORVSsTgcGjWoSJLG6Udco4FuVQXfky5K9H0Kf9RyXN9F1sIfrb
DKVGzNXZKJP3gStEKfAfR6BCMKYREDHPQNjVN2AYtrLZ1C/kjX/QD5RRmccYE9EyoLJidTPq
F6bGsuOu2VKcCjUbrq7cqMtZ59zI31YOccLkw3nnocwiDUNhixdmaZktpTO4MjlBmQ5qKexG
2CWwT2h72+SJDDPXBtI8rI9A0OZjkxS0v03dpc7aHtWYtntRlV5hItiYYCIwEBh5swZTJoJ/
drE1H9cdk2+z6eqPy4qJ4M8Tu+qNu4buXSCbUYX0cpSV7m09NguHxWU9OnodHHEL62AyzOLi
nUC3DrFBZYOhG6M8TAFi06REFLsGDAMdOnlQKsrmiueuZmDnP/7B8/FwMSnnxGdjKPQc+DBc
PcK/IaZOzecc98xggsme0JE8DJc2gQBTJyQq9ihbtqBBFqgEAiPF3/5putzDZMPlys47GzyP
8g8jKkzYj3uy4eoZBHUBXFnT0qKM5VR7l82eY+HquVH2G8Mm5WxiHOwF84ChmJ1I//tZXdTL
33uQBwiXIbuMYyAs7e6JvfsdjVz+heDKE43sZ9l5hH5Tz8zv4JpVL1dXbtTlrHNu5G8rhzhh
8uG88lB//WP/MszA7oOrQa/D3W7/LWwaMBaYDMZyphBj18AmZcxcrzAQYxgVyj+UUav0kC5W
Zo0RHkM4U6JhHJm1PVouK1vI6W/XNzgu7kqxoDiUbCptNl39cUkykWxMNX+m/jI9lymeSCUw
D6QPm/aro3EIqyZtxISRK0ZWRq3OrlFqW40gfeA/FUyl3FNtq7h5saYGacRWqStDJQ71ZbIB
KroJs82yEDefqdYD4A/i5MNggK1zqA99C3OhP5Gs6MOqynh1ArnKEl0O+7Rj1XNWg7oH5T/f
usSJf+Hz0PpZV8XP096GUWUWTNe2abrqTM2FVBJII+FBAxKIn7RQ7KUPdhhg9pwyD4KQZlxo
+e2ibjb0x2XBROIgXM3zSScfLsW2mmp5Zls9PDQKfzUe18nGnUp+M1OPMJI84mMm87B43JxH
+XKBtIEv10zWw2O68kDxmiBBggQJYiLvqDtAnDCXC4rgNNnucgUcNR9XvZzrngtR7XEptwPV
cXUabxPKhXCYQiOuBO9u2PuBi/N9TPIbIu3Z9v75b4NrLgeKfOHDLkGCBAkSvLvheUE2fwg7
kKizEiRIkCDBlJEwkQQJEiRIMGUkTCRBggQJEkwZCRNJkCBBggRTRsJEEiRIkCDBlJEwkQQJ
EiRIMGVErliP8EqQIEGCBO8iMIUXXuCn8uZC6pzfsS6EcKQ4icQJkw9JHvGR5BEfSR7xkeQR
H++WPHheCMRPFhsmSJAgQYIJ8Lwgmz+EHUhsIgkSJEiQYMpImEiCBAkSJJgiRP5/2vS8v186
Qk0AAAAASUVORK5CYII=
"""
)
