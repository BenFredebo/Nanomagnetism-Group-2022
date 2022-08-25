%Stripline Magnetic Field Calculation:

%Using derivation from Dissertation: Dmytro, C. (2006) High
%Frequency Behaviour of Magnetic Thin Film Elements
%For Microelectronics

%With user defined parameters for a magnetic stripline, the magnetic field 
%in the x and y directions surrounding the sample are calculated below:

%first takes user input for dimensions of stripline and current:

%I = input("Current through the Stripline (in A):");
%l = input("length of Stripline (in nanometers):");
%h = input("Height of Stripline (in nanometers):");

I=0.02;
l=300;
h=5;

%useful stripline dimensions:

a = l/2;
b = h/2;


%evenly distributed points in area of interest in both x and y:

xvec = linspace((-a-0.1*a), (a+0.1*a),50);
yvec = linspace((40*(-b)),(40*b),50);

%grid of x and y points for quiver plotting:
[X,Y] = meshgrid(xvec,yvec);


%following code creates a matrix of longitudinal mag-field strength
%by looping through each position vector element in x and y and evaluating
%the Hx field function at that point:

nx = numel(xvec);
hxgrid =zeros(nx);
for i=1:nx
for j=1:nx
    hxi = longfield(a,b,xvec(j),yvec(i),I);
    hxgrid(i,j)=hxi;

end
end

%similar as above but for the polar field component:

ny = numel(yvec);
hygrid =zeros(ny);
for i=1:ny
for j=1:ny
    hyi = polarfield(a,b,xvec(j),yvec(i),I);
    hygrid(i,j)=hyi;

end
end

%As the above field components are given in A/nm, the following converts
%them into the desired units of A/m:

hyfinal = hygrid * 10^9;
hxfinal = hxgrid * 10^9;



%plots a quiver plot of x,y positions and a rectangle emulating the
%stripline:

quiver(X,Y, hxgrid,hygrid,0.5)
rectangle("Position",[-a -b 2*a 2*b])
title("Magnetic field strength vector field around stripline")
xlabel('x-position in $nm$', 'Interpreter','latex')
ylabel('y-position in $nm$', 'Interpreter','latex')
legend("H-Vector field")




%Calculates the Vector components of longitudinal stripline magnetic field
%Using result from above dissertation:

function [Hx] = longfield(a,b,X,Y,I)
    %a is half of stripline length
    %b is half of stripline height
    %X is array of x positions 
    %Y is array of y positions
    %I is current value 
    %Returns longitudinal magnetic field component Hx


    p=pi;
    Hx = (-I/(8*p*a*b))* ...
        ((a-X)* ...
        (((1/2)*log(((b-Y)^2 + (a-X)^2)/((-b-Y)^2+(a-X)^2))) ...
        + ((b-Y)/(a-X))*atan((a-X)/(b-Y)) ...
        -((-b-Y)/(a-X))*atan((a-X)/(-b-Y))) ...
        -(-a-X)* ... %potentially +
        ((1/2)*log(((b-Y)^2 + (-a-X)^2)/((-a-X)^2+(-b-Y)^2)) ...
        + ((b-Y)/(-a-X))*atan((-a-X)/(b-Y)) ...
        -((-b-Y)/(-a-X))*atan((-a-X)/(-b-Y))));
end


%Calculates the Vector components of polar stripline magnetic field
%Using result from above dissertation:

function [Hy] = polarfield(a,b,X,Y,I)
    %a is half of stripline length
    %b is half of stripline height
    %X is array of x positions 
    %Y is array of y positions
    %I is current value 
    %Returns polar magnetic field component Hy

    p=pi;
    Hy = (I/(8*p*a*b))* ...
        (((b-Y)* ...
        (((1/2)*log(((b-Y)^2 + (a-X)^2)/((b-Y)^2+(-a-X)^2))) ...
        + ((a-X)/(b-Y))*atan((b-Y)/(a-X)) ...
        -((-a-X)/(b-Y))*atan((b-Y)/(-a-X)))) ...
        -((-b-Y)* ... %potentially +
        ((1/2)*log(((a-X)^2 + (-b-Y)^2)/((-a-X)^2+(-b-Y)^2)) ...
        + ((a-X)/(-b-Y))*atan((-b-Y)/(a-X)) ...
        -((-a-X)/(-b-Y))*atan((-b-Y)/(-a-X)))));
end




















    

