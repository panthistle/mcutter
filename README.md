## mcutter 0.1.6

### Mesh cutter add-on for Blender 2.83
\- inspired by the Pink Floyd song 'One of These Days' -

### About

Mad Cutter was developed in August 2020, while I was researching Blender's Python API.
I was looking to combine my research with a concrete example [add-on] and the idea to experiment with Blender's Boolean modifier in so-called non-destructive modelling seemed
appealing. The emphasis is more on the creative use of boolean operations rather than 
cut-precision. 
The add-on works on a Target mesh, using a set of temporary cutters that are generated on the fly. Undo/Redo are supported. It is NOT intended for use with objects that are particle system instances or objects with physics properties. It may be used with objects that have certain types of constraints and with parented objects.

### Installation

- Download the .zip archive to your hard drive 
- In Blender, open the Preferences window from the Edit menu
- In the Add-ons tab, click Install... and select the downloaded .zip file
- Enable the add-on

### Usage and features

Once enabled, the MCutter tab will appear in the UI (N panel) of Blender's 3D Viewport area. It is available in Object mode.

#### Start a Session

The start-up panel has a button which will create a copy of your original mesh. Because the add-on works with boolean modifiers, it makes sense to give it a source mesh with solid geometry. The 'Set Target' button will be disabled if there is no active mesh
in your scene or if the active mesh has no polygons. For more consistent results you should select both the 'Remove Modifiers' and 'Apply Scale' options but you may want to experiment. These options actually refer to the new copy, your original mesh object will not be affected.

#### Current Session Operations

After you click the 'Set Target' button, the add-on panel will display the available options for the current session. At this point, you will also notice that your 
original mesh is hidden and the working copy, the Target, is visible in the viewport. In addition, there is a new collection in Blender's Outliner area, named 
MCutter_TargetName_Temp. This is where all the temporary cutters are stored. If you look at the Properties area, you will see that a Boolean modifier has been added to the Target with the first cutter assigned.

Session Operations are grouped into four main categories.

**1. Display options:**  These are self-explanatory display options.

**2. Cutter stack:**  A list of all the cutters used in the current session. There are two buttons you use to add or remove cutters and you may also choose to copy the current settings to the new cutter. You can change the names of cutters by double-clicking on them. Note, that after you have added a cutter you must click the 'Update' button to see
the effect on the Target. This button activates the Update Operator and launches its Redo panel where you can update all the parameter settings of the Active Cutter.

There are three main cutter-profile styles. Rectangle, Ellipse and Wave. Each one of those has options which are enabled depending on the selected style. You change the cutter x/y/z dimensions by entering values in the respective Size fields.
You can further customize the profile with the Frame option. Position and Rotation of the cutter may be set to inherit from Target. There is also an option to array the cutter using either the radial array or the array modifiers.

**3. Restart - Finalize:**  To start a new session without saving changes, enable the 'Remove Temps' option and click on 'Restart'. This way, all temporary items, 
including the Target are completely removed. If you want to start a new session but keep the current objects, just uncheck the 'Remove Temps' option before clicking 'Restart'. The 'Finalize' button will apply the modifiers to the Target and remove the temporary collection and cutter objects.

**4. Cutter summary:**  When a cutter is selected in the stack, a summary of its  settings is displayed in this section. 

### Using MCutter as mesh generator

MCutter was not designed for the purpose of mesh generation. However you could use it to generate several types of custom mesh objects like cuboid, cylinder, wheel, ring, 
torus, and more.

### About Artefacts

The add-on does not impose restrictions on the parameter values you set. A consequence of this relative freedom is that you will occasionally observe artefacts (such as 
flying/hanging edges or split/missing faces) depending on the number of cutters, the number of iterations, the cutter position, and so on. In such cases, if you slightly 
change some parameters, the artefacts will go away and your result will be clean. Of course, there will be times when such artefacts are intentional or a happy serendipity?

### Note of Caution

Always remember to check your scene's polygon count before hitting the 'Add' or 'Update' buttons. There is no upper limit on the number of cutters you add to the stack, there 
are only soft upper limits (12 Radial steps, 20 iterations per Array modifier, and 90 segments per Resolution option) all of which you can override by typing a larger value. 
Be careful! Setting big values to those parameters will drastically increase the polygon count in your scene and this may slow down performance or even freeze Blender. Also,
keep in mind that MCutter works with a copy of your original mesh so you should avoid using it with heavy-geometry objects.
In short, MCutter madness can only go as far as your wisdom permits.

That's it. Now, you can put on some Pink Floyd and start cutting away..;)

Pan Thistle
