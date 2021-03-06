import maya.cmds as cmds
import pymel.core as pm
import re
import tak_lib
import tak_misc


if __name__ == "__main__":
    ### Blendshape Based Facial Rigging ###
    # set the facialList
    facialFullList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad', 'eyebrow_furrow',
    'eyelid_blink', 'eyelid_big', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad',
    'cheek_puff', 'cheek_suck',
    'nose_up', 'nose_down', 'nose_big', 'nose_sneer',
    'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmile', 'lip_openSmileBig', 'lip_angry', 'lip_angryBig', 'lipSync_A', 'lipSync_E', 'lipSync_I', 'lipSync_O', 'lipSync_U']

    facialLs = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
    'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
    'lip_wide', 'lip_narrow', 'lip_smile', 'lip_frown', 'lipSync_A', 'lipSync_E', 'lipSync_I', 'lipSync_O',
    ]


    facialCtrlLs = cmds.ls(sl = True)
    facialGrp = 'facial_bs_geo'

    for ctrl in facialCtrlLs:
        attrLs = cmds.listAttr(ctrl, keyable = True)
        trgNamePrefix = ctrl.rsplit('_ctrl')[0]
        for attr in attrLs:
            try:
                cmds.setAttr('%s.%s' %(ctrl, attr), 1)
                cmds.duplicate(facialGrp, rr = True, renameChildren = True, n = trgNamePrefix + '_' + attr)
                cmds.setAttr('%s.%s' %(ctrl, attr), 0)
            except:
                pass


    # Extract Facial Targets from Blendshape #
    bsNode = 'blendShape1'
    trgLs = cmds.listAttr(bsNode + '.w', multi = True)
    facialGrp = 'src_head_grp'

    for trg in trgLs:
        cmds.setAttr(bsNode + '.' + trg, 1)
        cmds.duplicate(facialGrp, renameChildren = True, n = trg)
        cmds.setAttr(bsNode + '.' + trg, 0)


    ### Joint Based Facial Rigging ###

    # Eyelid ikh locator align #
    import pymel.core as pm

    eyelidLocs = pm.ls(sl=True)
    for loc in eyelidLocs:

        ikh = loc.getChildren(type='ikHandle')[0]
        ikh.setParent(w=True)

        locZeroGrp = loc.getParent(generations=2)
        locZeroGrp.rotate.set(0,0,0)

        if 'lower' in loc.name():
           locZeroGrp.scaleY.set(-1)

        if 'rt_' in loc.name():
            locZeroGrp.scaleX.set(-1)

        ikh.setParent(loc)


    # Locator zero group scaleX set to -1 #
    locators = pm.ls(sl=True)
    for locator in locators:
        locChild = locator.getChildren(type='transform')[0]
        locChild.setParent(world=True)

        zeroGrpName = '%s_zero' % locator.name()
        pm.setAttr('%s.scaleX' % zeroGrpName, -1)

        locChild.setParent(locator)


    # Mirror zero group #
    zeroGrps = pm.ls(sl=True)
    searchStr = 'lf_'
    replaceStr = 'rt_'

    for zeroGrp in zeroGrps:
        zeroGrpTrans = zeroGrp.getTranslation()
        zeroGrpRotation = zeroGrp.getRotation()
        zeroGrpScale = zeroGrp.getScale()

        otherSideZeroGrpName = zeroGrp.replace(searchStr, replaceStr)
        otherSideZeroGrp = pm.PyNode(otherSideZeroGrpName)

        otherSideZeroGrp.setTranslation([-zeroGrpTrans.x, zeroGrpTrans.y, zeroGrpTrans.z])
        otherSideZeroGrp.setRotation([zeroGrpRotation.x, -zeroGrpRotation.y, -zeroGrpRotation.z])
        otherSideZeroGrp.setScale([-zeroGrpScale[0], zeroGrpScale[1], zeroGrpScale[2]])



    ### Facial Secondary ###

    # Eyelid #
    import pymel.core as pm
    import tak_misc

    # Normal eyelid
    selJnts = pm.selected()
    for jnt in selJnts:
        name = jnt.getChildren()[0].rsplit('_jnt')[0]
        
        ikh = pm.ikHandle(sj=jnt, ee=jnt.getChildren()[0], solver='ikSCsolver', n=name+'_ikh')[0]
        ikhWsPos = pm.xform(ikh, q=True, ws=True, t=True)
        
        loc = pm.spaceLocator(n=name+'_loc')
        loc.translate.set(ikhWsPos)
        ikh.setParent(loc)
        tak_misc.doGroup(loc.name(), '_zero')
        tak_misc.doGroup(loc.name(), '_auto')




    # Zipper Lip #
    import pymel.core as pm

    # Distribute constraint weight #
    selJnts = sorted(pm.ls(sl=True), reverse=True)
    segment = len(selJnts)-1
    fullWeight = 1.0
    increment = fullWeight/len(selJnts)

    weight = 1
    for jnt in selJnts:
        weight -= increment
        parentConstraintNode = jnt.getChildren()[0]
        parentConstraintNode.jaw_lockW0.set(weight*weight)


    # Zipper Lip Joints rampValuesNode Set Up #
    import pymel.core as pm
    jnts = pm.selected()

    driverJnts = ['jaw_ctrl', 'jaw_lock_jnt']
    drivenAttr = 'jaw_ctrlW1'

    rampValsNode = pm.createNode('rampValuesNode')
    rampValsNode.inValue.set(1.0)
    rampValsNode.numSamples.set(len(jnts))
    rampValsNode.ramp01[0].ramp01_Interp.set(3)
    rampValsNode.ramp01[0].ramp01_Position.set(0)
    rampValsNode.ramp01[0].ramp01_FloatValue.set(0)
    rampValsNode.ramp01[1].ramp01_Interp.set(3)
    rampValsNode.ramp01[1].ramp01_Position.set(0.6)
    rampValsNode.ramp01[1].ramp01_FloatValue.set(0.4)
    rampValsNode.ramp01[2].ramp01_Interp.set(3)
    rampValsNode.ramp01[2].ramp01_Position.set(1.0)
    rampValsNode.ramp01[2].ramp01_FloatValue.set(1.0)

    for jnt in jnts:
        parentConst = pm.parentConstraint(driverJnts, jnt, mo=True)
        rampValsNode.outValues[jnts.index(jnt)] >> parentConst.attr(drivenAttr)

    # Copy left constraint weight to right #
    selJnts = pm.ls(sl=True)
    for jnt in selJnts:
        parentConstraintNode = jnt.getChildren()[0]
        weightList = parentConstraintNode.getWeightAliasList()
        for weight in weightList:
            val = weight.get()
            oppositeWeight = pm.PyNode(weight.name().replace('lf_', 'rt_'))
            oppositeWeight.set(val)

    # Distribute SDK End Value #
    zipperLipJnts = pm.selected()
    zipperLipJnts.sort(key=lambda x:x.tx.get(), reverse=True)
    maxValue = 10.0
    increment = maxValue / len(zipperLipJnts)
    endValue = 0
    for jnt in zipperLipJnts:
        parentConst = jnt.getChildren(type='parentConstraint')[0]
        weightList = parentConst.getWeightAliasList()
        for weight in weightList:
            animCurve = weight.connections(type='animCurve')[0]
            animCurve.setUnitlessInput(1, endValue)
        endValue += increment


def createFacialList(facialGrp):
    facialList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
                      'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
                      'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmileBig', 'lip_angryBig', 'a', 'e',
                      'i', 'o']

    for item in facialList:
        cmds.duplicate(facialGrp, n=item, renameChildren=True)

    cmds.select(facialList, r=True)
    tak_misc.arrangeInAColumn()


def connectFacial(blendshapeNode='facial_bs'):
    """ Connect selected facial controls attributes to matching blendshape target """

    facialCtrlLs = cmds.ls(sl = True)

    for facialCtrl in facialCtrlLs:
        facialAttrLs = cmds.listAttr(facialCtrl, keyable = True)
        for facialAttr in facialAttrLs:
            facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)

            if cmds.objExists(blendshapeNode + '.' + facialBsTrgName):
                try:
                    cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialBsTrgName, f = True)
                except:
                    pass

            if 'lip' in facialCtrl:
                facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)
                if 'lip_lf' in facialBsTrgName:
                    facialBsTrgName = re.sub(r'lip_lf', 'lf_lip', facialBsTrgName)
                elif 'lip_rt' in facialBsTrgName:
                    facialBsTrgName = re.sub(r'lip_rt', 'rt_lip', facialBsTrgName)

                if cmds.objExists(blendshapeNode + '.' + facialBsTrgName):
                    try:
                        cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialBsTrgName, f = True)
                    except:
                        pass


### Facial Tertiary ###
def createCurveRig(name, numOfControls):
    """
    Create curve rig with selected edge loop

    Parameters:
        name: Rig name
        numOfControls: Number of local controls
    """

    # Convert edges to curve
    rawCurve = pm.PyNode(pm.polyToCurve(n=name+'_crv', form=2, degree=1)[0])

    # Create joints with rawCurve
    jnts = []
    for cv in rawCurve.cv:
        pm.select(cl=True)
        jnts.append(pm.joint(p=cv.getPosition(space='world'), radius=0.1))
    jnts = renameByPosition(name, jnts)

    # Rebuild curve and delete history
    newCrv = pm.rebuildCurve(rawCurve, spans=numOfControls-3, degree=3)[0]
    pm.delete(newCrv, ch=True)

    # Attach cluster to the curve cvs
    clusters = [pm.cluster(cv)[1] for cv in newCrv.cv]
    clusters = renameByPosition(name, clusters, suffix='clst')
    locators = []
    for clst in clusters:
        pm.select(clst, r=True)
        locators.append(tak_misc.locGrp())

    # Cleanup outliner
    jntGrp = pm.group(jnts, n=name+'_jnt_grp')
    locGrp = pm.group(locators, n=name+'_loc_grp')
    pm.group(jntGrp, locGrp, newCrv, n=name+'_system_grp')

def renameByPosition(name, transformList, suffix='bnd_jnt'):
    renamedList = []

    transformList.sort(key=lambda x:x.tx.get(), reverse=True) if 'rt_' in name else transformList.sort(key=lambda x:x.tx.get())
    for item in transformList:
        renamedList.append(item.rename('%s_%02d_%s' % (name, transformList.index(item)+1, suffix)))

    return renamedList


def createProjectedCurve(locators, nurbsSurface, name='projected_crv'):
    follicles = []
    positions = []
    for locator in locators:
        follicleTransform = createProjectedFollicle(locator, nurbsSurface)
        follicles.append(follicleTransform)
        positions.append(follicleTransform.getTranslation(space='world'))

    curve = pm.curve(d=3, p=positions, n=name)

    for follicle in follicles:
        decomposeMatrix = pm.createNode('decomposeMatrix', n='%s_decomposeMatrix' % follicle)
        follicle.worldMatrix >> decomposeMatrix.inputMatrix
        decomposeMatrix.outputTranslate >> curve.getShape().controlPoints[follicles.index(follicle)]


def createProjectedFollicle(locator, nurbsSurface):
    nurbsSurfaceShape = nurbsSurface.getShape()

    # Create nodes
    closestPointOnSurface = pm.createNode('closestPointOnSurface', n='%s_ClstPntOnSrfc' % locator.name())
    multiplyDivide = pm.createNode('multiplyDivide', n='%s_munDiv' % locator.name())
    follicleShape = pm.createNode('follicle', n='%s_follicleShape' % locator.name())
    follicleTransform = follicleShape.getTransform()

    # Connect nodes
    locator.getShape().worldPosition >> closestPointOnSurface.inPosition
    nurbsSurfaceShape.worldSpace >> closestPointOnSurface.inputSurface

    closestPointOnSurface.parameterU >> multiplyDivide.input1X
    closestPointOnSurface.parameterV >> multiplyDivide.input1Y
    nurbsSurfaceShape.minMaxRangeU.maxValueU >> multiplyDivide.input2X
    nurbsSurfaceShape.minMaxRangeV.maxValueV >> multiplyDivide.input2Y
    multiplyDivide.operation.set(2)

    multiplyDivide.outputX >> follicleShape.parameterU
    multiplyDivide.outputY >> follicleShape.parameterV
    nurbsSurfaceShape.worldSpace >> follicleShape.inputSurface
    nurbsSurfaceShape.worldMatrix >> follicleShape.inputWorldMatrix

    follicleShape.outTranslate >> follicleTransform.translate
    follicleShape.outRotate >> follicleTransform.rotate

    return follicleTransform


# Ball eyelid
def createIKHandles(bndJnts, baseJnt):
    ikhs = []
    for jnt in bndJnts:
        dupBaseJnt = baseJnt.duplicate(n=jnt.replace('_bnd_jnt', '_base_jnt'))[0]
        dupBaseJnt | jnt
        ikhs.append(pm.ikHandle(solver='ikSCsolver', sj=dupBaseJnt, ee=jnt, n=jnt.replace('_bnd_jnt', '_ikh'))[0])
    pm.select(ikhs, r=True)
