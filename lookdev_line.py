# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds


def GetAllToonShader(*args):
    shaderList = cmds.ls(materials=1)
    finalShaderList = [shader for shader in shaderList if cmds.nodeType(shader) == 'aiToon']
    return finalShaderList
    

def CreateSamplerSetup(*args):
    if not cmds.objExists('LineDepth_samplerInfo'):
        sampler = cmds.createNode('samplerInfo', n='LineDepth_samplerInfo')
    if not cmds.objExists('sampler_DIV'):
        sampler_div = cmds.createNode('floatMath', n='sampler_DIV')
        cmds.connectAttr(sampler+'.pointCameraZ', sampler_div+'.floatA')
        cmds.setAttr(sampler_div+'.operation', 3)
        cmds.setAttr(sampler_div+'.floatB', -100)
    
    return

def lineColorSetup(shaderList, *args):
    nodes = {}

    for toonShader in shaderList:
        edgeTonemapConnection = cmds.listConnections(f'{toonShader}.edgeTonemap', p=1)
        if edgeTonemapConnection:
            edgeTonemapConnection = edgeTonemapConnection[0]
        
        silhouetteTonemapConnection = cmds.listConnections(f'{toonShader}.silhouetteTonemap', p=1)
        if silhouetteTonemapConnection:
            silhouetteTonemapConnection = silhouetteTonemapConnection[0]
        
        if not cmds.objExists(f'switchTonemapLineDepth_{toonShader}'):
            switchTonemap = cmds.createNode('aiSwitch', n=f'switchTonemapLineDepth_{toonShader}')
            offTonemap = cmds.createNode('aiRampRgb', n=f'offTonemapLineDepth_{toonShader}')
            cmds.setAttr(offTonemap+'.ramp[0].ramp_Color', 1,1,1)
            cmds.setAttr(offTonemap+'.ramp[1].ramp_Color', 1,1,1)
            cmds.connectAttr(offTonemap+'.outColor', switchTonemap+'.input1')
            print(f'creating switchTonemap for {toonShader}')
        
        if edgeTonemapConnection:
            if not f'switchTonemapLineDepth_{toonShader}' in edgeTonemapConnection:
                cmds.connectAttr(edgeTonemapConnection, f'switchTonemapLineDepth_{toonShader}.input0', f=1)
                cmds.connectAttr(f'switchTonemapLineDepth_{toonShader}.outColor', f'{toonShader}.edgeTonemap', f=1)
        
        if silhouetteTonemapConnection:
            if not f'switchTonemapLineDepth_{toonShader}' in silhouetteTonemapConnection:
                cmds.connectAttr(silhouetteTonemapConnection, f'switchTonemapLineDepth_{toonShader}.input0', f=1)
                cmds.connectAttr(f'switchTonemapLineDepth_{toonShader}.outColor', f'{toonShader}.silhouetteTonemap', f=1)
        
        
        for edge in ['edge', 'silhouette']:
            colorConnection = cmds.listConnections(f'{toonShader}.{edge}Color', p=1)
            if colorConnection:
                colorConnection = colorConnection[0]
            
                if f'switch{edge.title()}LineDepth_{toonShader}' in colorConnection:
                    print(f'{toonShader} {edge} line color setup already exists')
                    continue
            
            nodes[toonShader] = {}
            switch = cmds.createNode('aiSwitch', n=f'switch{edge.title()}LineDepth_{toonShader}')
            nodes[toonShader]['switch'] = switch
            if colorConnection:
                cmds.connectAttr(colorConnection, switch+'.input0')
                print(f'connecting {edge} {colorConnection} to {switch}')
            else:
                color = cmds.getAttr(toonShader+'.silhouetteColor')[0]
                colorNode = cmds.createNode('colorConstant', n=f'{edge}LineColor_{toonShader}')
                nodes[toonShader]['colorNode'] = colorNode
                cmds.setAttr(colorNode+'.inColor', color[0], color[1], color[2])
                cmds.connectAttr(colorNode+'.outColor', switch+'.input0')
                print(f'saving {edge} color in {colorNode}')
            cmds.connectAttr(switch+'.outColor', f'{toonShader}.{edge}Color', f=1)
            
            samplerColor = cmds.createNode('colorConstant', n=f'{edge}SamplerColor_{toonShader}')
            nodes[toonShader]['samplerColor'] = samplerColor
            cmds.connectAttr(samplerColor+'.outColor', switch+'.input1')
        
            print(f'DONE {edge} line color', toonShader)
    
    return nodes

def CreatelineColorSetup(*args):
    shaderList = GetAllToonShader()
    nodes = lineColorSetup(shaderList)
  
def lineWidthSetup(shaderList,*args):
    nodes = {}

    for toonShader in shaderList:
        for edge in ['edge', 'silhouette']:
            widthConnection = cmds.listConnections(f'{toonShader}.{edge}WidthScale', p=1)
            if widthConnection:
                widthConnection = widthConnection[0]
            
                if f'mult{edge.title()}LineWidth_{toonShader}' in widthConnection:
                    print(f'{toonShader} {edge} line width setup already exists')
                    continue
        
            multiply = cmds.createNode('floatMath', n=f'mult{edge.title()}LineWidth_{toonShader}')
            cmds.setAttr(multiply+'.operation', 2)
            if widthConnection:
                cmds.connectAttr(widthConnection, multiply+'.floatA')
                print(f'connecting {edge} {widthConnection} to {multiply}')
            else:
                value = cmds.getAttr(toonShader+'.silhouetteWidthScale')
                cmds.setAttr(multiply+'.floatA', value)
                print(f'saving {edge} width in {multiply}')
            cmds.connectAttr(multiply+'.outFloat', f'{toonShader}.{edge}WidthScale', f=1)
            
            normalize = cmds.createNode('floatMath', n=f'normalize{edge.title()}LineWidth_{toonShader}')
            cmds.setAttr(normalize+'.floatA', 1)
            cmds.setAttr(normalize+'.operation', 1)
            cmds.connectAttr(normalize+'.outFloat', multiply+'.floatB', f=1)
            
            nodes['toonShader'] = {'multiply':multiply, 'normalize':normalize}
        
            print(f'DONE {edge} line width', toonShader)
    
    return nodes

def CreatelineWidthSetup(*args):
    shaderList = GetAllToonShader()
    nodes = lineWidthSetup(shaderList)
  
def ConnectSamplerToLineColorSetup(shaderList=[], *args):
    CreateSamplerSetup()
    if not shaderList:
        shaderList = GetAllToonShader()
    
    for shader in shaderList:
        for edge in ['edge', 'silhouette']:
            try:
                cmds.connectAttr('sampler_DIV.outFloat', f'{edge}SamplerColor_{shader}.inColorR', f=1)
                cmds.connectAttr('sampler_DIV.outFloat', f'{edge}SamplerColor_{shader}.inColorG', f=1)
                cmds.connectAttr('sampler_DIV.outFloat', f'{edge}SamplerColor_{shader}.inColorB', f=1)
                print(f'{shader} {edge} line color setup connected successfully')
            except:
                continue

def ConnectSamplerToLineWidthSetup(shaderList=[], *args):
    CreateSamplerSetup()
    if not shaderList:
        shaderList = GetAllToonShader()
    
    for shader in shaderList:
        for edge in ['edge', 'silhouette']:
            cmds.connectAttr('sampler_DIV.outFloat', f'normalize{edge.title()}LineWidth_{shader}.floatB', f=1)
            print(f'{shader} {edge} line width setup connected successfully')

def toggleSwitch(value=None, *args):
    shaderList = GetAllToonShader()
    
    for edge in ['edge', 'silhouette']:
        if not value:
            value = 1-cmds.getAttr(f'switch{edge.title()}LineDepth_{shaderList[0]}.index')
        for shader in shaderList:
            try:
                cmds.setAttr(f'switch{edge.title()}LineDepth_{shader}.index', value)
                cmds.setAttr(f'switchTonemapLineDepth_{shader}.index', value)
                print(f'{shader} {edge} switch is set to {value}')
                
            except:
                continue

def selectSamplerDiv(*args):
    cmds.select('sampler_DIV')