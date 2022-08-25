%Script calculates and plots the magnetic field strength vectors
%surrounding a disk cross section with a given radius a and applied current
%I. 



%radius of disk cross section in nanometers
a = 100;

%current through disk cross section in A
I=0.02;


%Plotting range and number of arrows, and matrix representation of (x,y)
%ranges:
ticks = linspace(-20*a,20*a,40);
[XX,YY] = meshgrid(ticks,ticks);


%magnetic field components produced by disk:
hx = (I/(2*pi*a))*(YY)./(XX.^2+YY.^2);
hy = (I/(2*pi*a))*(-XX)./(XX.^2+YY.^2);


%plots  quiver plot of field strength vectors centred at (0,0) with a disk
%superimposed to show the position and relative size of the disk
quiver(ticks,ticks,hx,hy, 1.2,"color",[0.7,0.6,0.9])
pos = [-a -a 2*a 2*a];
rectangle('Position',pos,'Curvature',[1 1])
xlabel("x-position in $nm$", "Interpreter","latex")
ylabel("y-position in $nm$", "Interpreter","latex")
title("Vector magnetic field surrounding circular current carrying disk")
legend("Relative field strength")
axis equal




%Calculates the x Vector component of magnetic field surrounding a circular
%disk of radius a:

function [Hx] = xfield(a,X,Y,I)
    %a is the radius of the disk
    %X is x position
    %Y is y position
    %I is the value of current through the surface 
    %Returns x component of magnetic field


    p=pi;
    Hx = (I/a*p)*(1/((X^2+Y^2))) *(Y);
end


%Calculates the y Vector component of magnetic field surrounding a circular
%disk of radius a:

function [Hx] = yfield(a,X,Y,I)
    %a is the radius of the disk
    %X is x position
    %Y is y position
    %I is the value of current through the surface 
    %Returns x component of magnetic field


    p=pi;
    Hx = (I/a*p)*(1/((X^2+Y^2))) *(-X);
end