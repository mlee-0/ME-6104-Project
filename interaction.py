"""
Mouse-click interactions with geometry.
"""

import vtk


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    def __init__(self):
        # Create the picker object used to select geometry on the screen.
        self.picker = vtk.vtkPropPicker()
        # Set the tolerance of picking operations, as a fraction of rendering window size (diagonal).
        # self.picker.SetTolerance(0.001)

        # Set functions to be called when mouse events occur.
        self.AddObserver("LeftButtonPressEvent", self.left_mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
    
    def left_mouse_press(self, obj, event):
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        # Perform picking and get the picked actor if it was picked.
        picker = vtk.vtkPointPicker()
        if picker.Pick(position[0], position[1], 0, self.GetDefaultRenderer()):
            actor = picker.GetActor()
            actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self.GetInteractor().Render()

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonDown()

    def left_mouse_release(self, obj, event):
        pass

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonUp()

    def mouse_move(self, obj, event):
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        # Fix the position by reduce each coordinate by half.
        position = [_/2 for _ in position]
        # Perform picking and get the picked actor if it was picked.
        if self.picker.Pick(position[0], position[1], 0, self.GetDefaultRenderer()):
            actor = self.picker.GetActor()
            # actor.GetProperty().SetColor(0.5, 0.5, 0.5)
            print(self.picker.GetPickPosition())
            self.HighlightProp(actor)
        print(position)
        self.GetInteractor().Render()
        
        # Run the default superclass function after custom behavior defined above.
        self.OnMouseMove()