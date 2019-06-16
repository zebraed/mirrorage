import pymel.core as pm
import math

from collections import OrderedDict

class SoftIK_gui(object):
    def __init__(self):
        self.core = SoftIK_core()
    
    def cmd(self, *args):
        self.core.execute()
    
    def execute(self, *args):
        if pm.window('softIK', q=True, ex=True):
            pm.deleteUI('softIK')

        with pm.window('softIK', t='Attach softIK', w=240, h=40, s=True, mnb=False, mxb=False):
            with pm.columnLayout(adj=True):
                pm.text(l='set node', al='center')
                pm.textField("name")
                pm.textField("ctrl_name")
                pm.textField("ikh_name")
                    
                pm.checkBox("stretch")
                pm.text(l='primary axis', al='center')
                pm.radioButtonGrp("primary_axis", labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3)
                pm.text(l='up axis', al='center')
                pm.radioButtonGrp("up_axis" ,labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3)
                pm.separator()
                pm.button('attach', c=self.cmd)


class SoftIK_core(object):
    #calculate and 
        
    def execute(self):
        self.set_values()
        self.set_joints()
        self.sum_jntLength()
        self.solve_axis()
        self.get_IKh_dist()
        self.createNodesNetWork()

    
    @staticmethod
    def _getPy(arg):
        if isinstance(arg, (str, unicode)):
            return pm.PyNode(arg)
        elif isinstance(arg, (set, list, tuple)):
            return [ pm.PyNode(node) for node in arg ]
        else:
            return arg
            
            
    @staticmethod
    def _wPos(arg):
        return pm.xform(arg, q=1, piv=1, ws=1)


    @staticmethod
    def vec_dist(p1, p2):
        x = p2[0] - p1[0]
        y = p2[1] - p1[1]
        z = p2[2] - p1[2]
        return [ x, y, z ]
        
        
    @staticmethod
    def vec_mag(vec):
        return (math.sqrt(sum(v ** 2 for v in vec )))


    def givenSaffix(self):
        pass

       
    def set_values(self):
        self.name      = pm.textField('name',      q=1, tx=1)
        self.ctrl_name = pm.textField('ctrl_name', q=1, tx=1)
        self.ikh_name  = pm.textField('ikh_name',  q=1, tx=1)
        
        self.stretch   = pm.checkBox('stretch',    q=1, v=1)
        
        self.up_axis      = pm.radioButtonGrp('up_axis',      q=1, sl=1)
        self.primary_axis = pm.radioButtonGrp('primary_axis', q=1, sl=1)
 
        
    def set_joints(self):
        ikh = self._getPy(self.ikh_name)
        s_joint    = pm.listConnections(ikh.startJoint )
        e_effector = pm.listConnections(ikh.endEffector)
        e_joint    = pm.listConnections(e_effector, d=0, s=1)[0]

        self.jts = []
        self.jts.extend(s_joint + pm.listRelatives(s_joint, ad=1, type='joint')[::-1])
        
        self.s_pos = self._wPos(self.jts[0])
        self.e_pos = self._wPos(self.jts[-1])
        
    
    def sum_jntLength(self):
        i = 0
        self.dchain = 0
        self.jnt_length = len(self.jts)
        
        while(i < self.jnt_length - 1):
            a = self._wPos(self.jts[i])
            b = self._wPos(self.jts[i+1])
            
            v = self.vec_dist(a, b)
            self.dchain += self.vec_mag(v)
            i += 1
    
    
    def get_IKh_dist(self):
        v = self.vec_dist(self.g_point, self.e_pos[0:3])
        self.def_pos = self.vec_mag(v)
        
        if ((self.up_axis == 'X') and (self.e_pos[0] < 0 ) ):
            self.def_pos = self.def_pos * -1
        
        elif ((self.up_axis == 'Y') and (self.e_pos[1] < 0 ) ):
            self.def_pos = self.def_pos * -1
        
        elif ((self.up_axis == 'Z') and (self.e_pos[2] < 0 ) ):
            self.def_pos = self.def_pos * -1


    def solve_axis(self):

        if self.primary_axis == 1:
            self.primary_axis = 'X' 
            
        elif self.primary_axis == 2:
            self.primary_axis = 'Y'
        
        elif self.primary_axis == 3:
            self.primary_axis = 'Z'

        if self.up_axis == 1:
            self.up_axis = 'X' 
            self.g_point = (0, self.e_pos[1], self.e_pos[2])
            
        elif self.up_axis == 2:
            self.up_axis = 'Y'
            self.g_point = (self.e_pos[0], 0, self.e_pos[2])
            
        elif self.up_axis == 3:
            self.up_axis = 'Z'
            self.g_point = (self.e_pos[0], self.e_pos[1], 0)


    def createNodesNetWork(self):
        #create maya nodes.
        
        #create distance node.
        startLoc = pm.spaceLocator(n=self.name + 'StartDist_loc')
        pm.xform(startLoc, t=self.s_pos[0:3], ws=1)
        endLoc   = pm.spaceLocator(n=self.name + 'EndDist_loc')
        pm.xform(endLoc, t=self.e_pos[0:3], ws=1)
        
        #parent constraint
        pm.parentConstraint(self.ctrl_name, endLoc, mo=1, w=1)
        
        x_db = pm.createNode('distanceBetween', n=self.name + 'X_db', ss=1)
        startLoc.t >> x_db.point1
        endLoc.t   >> x_db.point2
        
        #add attr and set driven to controllers.
        pm.addAttr(self.ctrl_name, ln='dSoft', at='double', min=0.001, max=2, dv=0.001, k=1)
        pm.addAttr(self.ctrl_name, ln='softIK', at='double', min=0, max=20, dv=0, k=1)
        
        pm.setDrivenKeyframe(self.ctrl_name + '.dSoft', cd=self.ctrl_name + '.softIK')
        pm.setAttr(self.ctrl_name + '.softIK', 20)
        pm.setAttr(self.ctrl_name + '.dSoft',  2)
        pm.setDrivenKeyframe(self.ctrl_name + '.dSoft', cd=self.ctrl_name + '.softIK')
        pm.setAttr(self.ctrl_name + '.softIK', 0)
        pm.setAttr(self.ctrl_name + '.dSoft', l=1, k=0, cb=0)
                
        #create operarotr nodes for softIK.
        softIk_nodes = OrderedDict()
        softIk_nodes['nodes'] = (
            {'name' : 'Da_pma'            ,'type' : 'plusMinusAverage'  , 'operation': 2 } ,
            {'name' : 'Xmda_pma'          ,'type' : 'plusMinusAverage'  , 'operation': 2 } ,
            {'name' : 'NegXm_md'          ,'type' : 'multiplyDivide'    , 'operation': 1 } ,
            
            {'name' : 'DivDsoft_md'       ,'type' : 'multiplyDivide'    , 'operation': 2 } ,
            {'name' : 'PowE_md'           ,'type' : 'multiplyDivide'    , 'operation': 3 } ,
            {'name' : 'MinusOnePowE_pma'  ,'type' : 'plusMinusAverage'  , 'operation': 2 } ,
            {'name' : 'TimesDsoft_md'     ,'type' : 'multiplyDivide'    , 'operation': 1 } ,
            
            {'name' : 'PlusDa_pma'        ,'type' : 'plusMinusAverage'  , 'operation': 1 } ,
            {'name' : 'Da_cond'           ,'type' : 'condition'         , 'operation': 5 } ,
            {'name' : 'DistDiff_pma'      ,'type' : 'plusMinusAverage'  , 'operation': 2 } ,
            {'name' : 'DefPos_pma'        ,'type' : 'plusMinusAverage'  , 'operation': 2 } ,
        )
        
        softIkVariable_dict = OrderedDict()
        for d in softIk_nodes['nodes']:
            softIkVariable_dict[d['name']] = pm.createNode(d['type'], n=self.name + d['name'], ss=1)
            softIkVariable_dict[d['name']].operation.set(d['operation'])
        
        if self.up_axis == 'X' and self.def_pos > 0:
            softIkVariable_dict['DefPos_pma'].operation.set(1)
            
        elif self.up_axis == 'Y':
            softIkVariable_dict['DefPos_pma'].operation.set(2)
        
        elif self.up_axis == 'Z' and self.def_pos < 0:
            softIkVariable_dict['DefPos_pma'].operation.set(1)
        
        
        #set unique flag value and connections.
        cn  = self._getPy(self.ctrl_name)
        ikh = self._getPy(self.ikh_name)
        
        softIkVariable_dict['Da_pma'].input1D[0].set(self.dchain)
        
        cn.dSoft                                         >> softIkVariable_dict['Da_pma'].input1D[1]
        
        x_db.distance                                    >> softIkVariable_dict['Xmda_pma'].input1D[0]
        softIkVariable_dict['Da_pma'].output1D           >> softIkVariable_dict['Xmda_pma'].input1D[1]
        
        softIkVariable_dict['Xmda_pma'].output1D         >> softIkVariable_dict['NegXm_md'].input1X
        
        softIkVariable_dict['NegXm_md'].input2X.set(-1)
        
        softIkVariable_dict['NegXm_md'].outputX          >> softIkVariable_dict['DivDsoft_md'].input1X
        cn.dSoft                                         >> softIkVariable_dict['DivDsoft_md'].input2X
        
        
        softIkVariable_dict['PowE_md'].input1X.set(2.718281828)
        
        softIkVariable_dict['DivDsoft_md'].outputX       >> softIkVariable_dict['PowE_md'].input2X
        
        
        softIkVariable_dict['MinusOnePowE_pma'].input1D[0].set(1)
        
        softIkVariable_dict['PowE_md'].outputX           >> softIkVariable_dict['MinusOnePowE_pma'].input1D[1]
        
        softIkVariable_dict['MinusOnePowE_pma'].output1D >> softIkVariable_dict['TimesDsoft_md'].input1X
        cn.dSoft                                         >> softIkVariable_dict['TimesDsoft_md'].input2X
        
        softIkVariable_dict['TimesDsoft_md'].outputX     >> softIkVariable_dict['PlusDa_pma'].input1D[0]
        softIkVariable_dict['Da_pma'].output1D           >> softIkVariable_dict['PlusDa_pma'].input1D[1]
        
        softIkVariable_dict['Da_pma'].output1D           >> softIkVariable_dict['Da_cond'].firstTerm
        x_db.distance                                    >> softIkVariable_dict['Da_cond'].secondTerm
        x_db.distance                                    >> softIkVariable_dict['Da_cond'].colorIfFalseR
        softIkVariable_dict['PlusDa_pma'].output1D       >> softIkVariable_dict['Da_cond'].colorIfTrueR
        
        softIkVariable_dict['Da_cond'].outColorR         >> softIkVariable_dict['DistDiff_pma'].input1D[0]
        x_db.distance                                    >> softIkVariable_dict['DistDiff_pma'].input1D[1]
        
        softIkVariable_dict['DefPos_pma'].input1D[0].set(self.def_pos)
        
        softIkVariable_dict['DistDiff_pma'].output1D     >> softIkVariable_dict['DefPos_pma'].input1D[1]
        
        softIkVariable_dict['DefPos_pma'].output1D       >> ikh.attr('translate' + self.up_axis)
        
        
        if self.stretch:
            pm.addAttr(self.ctrl_name, ln='stretch', at='double', min=0, max=10, dv=10, k=1)
            
            stretchIk_nodes = OrderedDict()
            stretchIk_nodes['nodes'] =(
                {'name' : 'SoftRatio_md'      ,'type' : 'multiplyDivide'      } ,
                {'name' : 'Stretch_blend'     ,'type' : 'blendColors'         } ,
                {'name' : 'StretchSwitch_mdl' ,'type' : 'multDoubleLinear'    } ,
            )
            
            stretchIkVariable_dict = OrderedDict()
            for d in stretchIk_nodes['nodes']:
                stretchIkVariable_dict[d['name']] = pm.createNode(d['type'], n=self.name + d['name'], ss=1)
            stretchIkVariable_dict['SoftRatio_md'].operation.set(2)
            stretchIkVariable_dict['Stretch_blend'].color2R.set(1)
            stretchIkVariable_dict['Stretch_blend'].color1G.set(self.def_pos)
            stretchIkVariable_dict['StretchSwitch_mdl'].input2.set(0.1)
            
            cn.stretch                                          >> stretchIkVariable_dict['StretchSwitch_mdl'].input1
            
            stretchIkVariable_dict['StretchSwitch_mdl'].output  >> stretchIkVariable_dict['Stretch_blend'].blender
            
            x_db.distance                                       >> stretchIkVariable_dict['SoftRatio_md'].input1X
            softIkVariable_dict['Da_cond'].outColorR            >> stretchIkVariable_dict['SoftRatio_md'].input2X
            
            softIkVariable_dict['DefPos_pma'].output1D          >> stretchIkVariable_dict['Stretch_blend'].color2G
            stretchIkVariable_dict['SoftRatio_md'].outputX      >> stretchIkVariable_dict['Stretch_blend'].color1R
            
            stretchIkVariable_dict['Stretch_blend'].outputG     >> ikh.attr('translate' + self.up_axis)
            i = 0
            while(i < self.jnt_length - 1):
                stretchIkVariable_dict['Stretch_blend'].outputR >> self.jts[i].attr('scale' + self.primary_axis)
                i += 1
        
        pm.select(cl=1)