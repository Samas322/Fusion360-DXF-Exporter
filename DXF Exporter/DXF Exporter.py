import adsk.core, adsk.fusion, adsk.cam, traceback, os, tkinter
from tkinter import filedialog

app = adsk.core.Application.get()
ui = app.userInterface

WORKSPACE_ID = 'FusionSolidEnvironment'
TOOLBARTAB_ID = "ToolsTab"
TOOLBARPANEL_ID = "SolidScriptsAddinsPanel"
CMD_ID = "DXF Export"

handlers = []
_handlers = []

class SketchExporterCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False

            onExecute = SketchExporterCommandExecuteHandler()
            cmd.execute.add(onExecute)

            onDestroy = SketchExporterCommandDestroyHandler()
            cmd.destroy.add(onDestroy)

            # Keep the handlers referenced
            handlers.append(onExecute)
            handlers.append(onDestroy)

            # Define the command inputs
            inputs = cmd.commandInputs
            selInput = inputs.addSelectionInput('sketchSelection', 'Select sketches', 'Select sketches to export')
            selInput.addSelectionFilter('Sketches')
            selInput.setSelectionLimits(0, 0)  # Allow selecting multiple sketches

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class SketchExporterCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs

            sketchInput = inputs.itemById('sketchSelection')
            selected_sketches = [sketchInput.selection(i).entity for i in range(sketchInput.selectionCount)]
            if not selected_sketches:
                ui.messageBox('No sketch selected.')
                return  # No sketch selected, exit

            dxf_folder_path = self.get_folder_path()
            if not dxf_folder_path:
                return  # No folder selected, exit

            for sketch in selected_sketches:
                self.export_sketch(sketch, dxf_folder_path)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def export_sketch(self, sketch, dxf_folder_path):
        try:
            sketch_name = sketch.name
            dxf_file_path = os.path.join(dxf_folder_path, f"{sketch_name}.dxf")
            sketch.saveAsDXF(dxf_file_path)

        except:
            if ui:
                ui.messageBox('Failed to export sketch:\n{}'.format(traceback.format_exc()))

    def get_folder_path(self):
        root = tkinter.Tk()
        root.withdraw()  # Hide the root window
        folder_path = filedialog.askdirectory()
        root.destroy()
        return folder_path

class SketchExporterCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            pass
            #adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    global _handlers

    cmdDef = ui.commandDefinitions.itemById(CMD_ID)
    if not cmdDef:
        cmdDef = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_ID, CMD_ID, ".\\")
    onCommandCreated = scriptExecuteHandler()
    cmdDef.commandCreated.add(onCommandCreated)
    _handlers.append(onCommandCreated)

    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    toolbar_tab = workspace.toolbarTabs.itemById(TOOLBARTAB_ID)
    panel = toolbar_tab.toolbarPanels.itemById(TOOLBARPANEL_ID)
    control = panel.controls.addCommand(cmdDef)
    control.isPromoted = True


def stop(context):
    global _handlers
    _handlers = []

    try:
        ui.commandDefinitions.itemById(CMD_ID).deleteMe()
    except:
        pass

    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    toolbar_tab = workspace.toolbarTabs.itemById(TOOLBARTAB_ID)
    panel = toolbar_tab.toolbarPanels.itemById(TOOLBARPANEL_ID)
    try:
        panel.controls.itemById(CMD_ID).deleteMe()
    except:
        pass

class scriptExecuteHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        
        self._onCommandCreated = None

    def notify(self, eventArgs: adsk.core.CommandCreatedEventArgs) -> None:
        try:
            commandDefinitions = ui.commandDefinitions
            cmdDef = commandDefinitions.itemById('SketchExporter')
            if not cmdDef:
                cmdDef = commandDefinitions.addButtonDefinition('SketchExporter', 'Export sketches in DXF', 'Select sketches to export to DXF files.')

            if not self._onCommandCreated:
                self._onCommandCreated = SketchExporterCommandCreatedHandler()
                cmdDef.commandCreated.add(self._onCommandCreated)
                handlers.append(self._onCommandCreated)

            inputs = adsk.core.NamedValues.create()
            cmdDef.execute(inputs)

            adsk.autoTerminate(False)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        app.log(f'{eventArgs.firingEvent.sender.name} executed!')
