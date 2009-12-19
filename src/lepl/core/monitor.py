
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Support for classes that monitor the execution process (for example, managing 
resources and tracing program flow).

See `trampoline()`.
'''


class ValueMonitor(object):
    '''
    An interface expected by `trampoline()`, called to track data flow.
    '''
    
    def next_iteration(self, epoch, value, exception, stack):
        '''
        Called at the start of each iteration.
        '''
        pass
    
    def before_next(self, generator):
        '''
        Called before invoking ``next`` on a generator.
        '''
        pass
    
    def after_next(self, value):
        '''
        Called after invoking ``next`` on a generator.
        '''
        pass
    
    def before_throw(self, generator, value):
        '''
        Called before invoking ``throw`` on a generator. 
        '''
        pass
    
    def after_throw(self, value):
        '''
        Called after invoking ``throw`` on a generator. 
        '''
        pass
    
    def before_send(self, generator, value):
        '''
        Called before invoking ``send`` on a generator. 
        '''
        pass
    
    def after_send(self, value):
        '''
        Called after invoking ``send`` on a generator. 
        '''
        pass
    
    def exception(self, value):
        '''
        Called when an exception is caught (instead of any 'after' method).
        '''
        pass
    
    def raise_(self, value):
        '''
        Called before raising an exception to the caller.
        '''
        pass
    
    def yield_(self, value):
        '''
        Called before yielding a value to the caller.
        '''
        pass
    
    
class StackMonitor(object):
    '''
    An interface expected by `trampoline()`, called to track stack growth.
    '''
    
    def push(self, generator):
        '''
        Called before adding a generator to the stack.
        '''
        pass
    
    def pop(self, generator):
        '''
        Called after removing a generator from the stack.
        '''
        pass
    
    
class ActiveMonitor(StackMonitor):
    '''
    A `StackMonitor` implementation that allows matchers that implement the
    interface on_push/on_pop to be called. 
    
    Generators can interact with active monitors if:
    
      1. The monitor extends this class
    
      2. The matcher has a monitor_class attribute whose value is equal to (or a 
         subclass of) the monitor class it will interact with
    '''
    
    def push(self, generator):
        '''
        Called when a generator is pushed onto the trampoline stack.
        '''
        if hasattr(generator.matcher, 'monitor_class') and \
                isinstance(self, generator.matcher.monitor_class):
            generator.matcher.on_push(self)
        
    def pop(self, generator):
        '''
        Called when a generator is popped from the trampoline stack.
        '''
        if hasattr(generator.matcher, 'monitor_class') and \
                isinstance(self, generator.matcher.monitor_class):
            generator.matcher.on_pop(self)
        

class MultipleValueMonitors(ValueMonitor):
    '''
    Combine several value monitors into one.
    '''
    
    def __init__(self, monitors=None):
        super(MultipleValueMonitors, self).__init__()
        self._monitors = [] if monitors is None else monitors
        
    def append(self, monitor):
        '''
        Add another monitor to the chain.
        '''
        self._monitors.append(monitor)
        
    def __len__(self):
        return len(self._monitors)
    
    def next_iteration(self, epoch, value, exception, stack):
        '''
        Called at the start of each iteration.
        '''
        for monitor in self._monitors:
            monitor.next_iteration(epoch, value, exception, stack)
    
    def before_next(self, generator):
        '''
        Called before invoking ``next`` on a generator.
        '''
        for monitor in self._monitors:
            monitor.before_next(generator)
    
    def after_next(self, value):
        '''
        Called after invoking ``next`` on a generator.
        '''
        for monitor in self._monitors:
            monitor.after_next(value)
    
    def before_throw(self, generator, value):
        '''
        Called before invoking ``throw`` on a generator. 
        '''
        for monitor in self._monitors:
            monitor.before_throw(generator, value)
    
    def after_throw(self, value):
        '''
        Called after invoking ``throw`` on a generator. 
        '''
        for monitor in self._monitors:
            monitor.after_throw(value)
    
    def before_send(self, generator, value):
        '''
        Called before invoking ``send`` on a generator. 
        '''
        for monitor in self._monitors:
            monitor.before_send(generator, value)
    
    def after_send(self, value):
        '''
        Called after invoking ``send`` on a generator. 
        '''
        for monitor in self._monitors:
            monitor.after_send(value)
    
    def exception(self, value):
        '''
        Called when an exception is caught (instead of any 'after' method).
        '''
        for monitor in self._monitors:
            monitor.exception(value)
    
    def raise_(self, value):
        '''
        Called before raising an exception to the caller.
        '''
        for monitor in self._monitors:
            monitor.raise_(value)
    
    def yield_(self, value):
        '''
        Called before yielding a value to the caller.
        '''
        for monitor in self._monitors:
            monitor.yield_(value)
    

class MultipleStackMonitors(StackMonitor):
    '''
    Combine several stack monitors into one.
    '''
    
    def __init__(self, monitors=None):
        super(MultipleStackMonitors, self).__init__()
        self._monitors = [] if monitors is None else monitors
        
    def append(self, monitor):
        '''
        Add another monitor to the chain.
        '''
        self._monitors.append(monitor)
        
    def __len__(self):
        return len(self._monitors)
    
    def push(self, value):
        '''
        Called before adding a generator to the stack.
        '''
        for monitor in self._monitors:
            monitor.push(value)
    
    def pop(self, value):
        '''
        Called after removing a generator from the stack.
        '''
        for monitor in self._monitors:
            monitor.pop(value)


def prepare_monitors(monitor_factories):
    '''
    Take a list of monitor factories and return an active and a passive
    monitor (or None, if none given).
    '''
    stack, value = MultipleStackMonitors(), MultipleValueMonitors()
    monitor_factories = [] if monitor_factories is None else monitor_factories
    for monitor_factory in monitor_factories:
        monitor = monitor_factory()
        if isinstance(monitor, StackMonitor):
            stack.append(monitor)
        if isinstance(monitor, ValueMonitor):
            value.append(monitor)
    return (stack if stack else None, value if value else None)
