%Script calculates and plots the magnetic field strength vectors
%surrounding a disk cross section with a given radius a and applied current
%I. 



%radius of disk cross section in nanometers
a = 100;

%current through disk cross section in A
I=0.02;


%Plotting range and number of arrows, and matrix representation of (x,y)
%ranges:
ticks = linspace(-15*a,15*a,30);
[XX,YY] = meshgrid(ticks,ticks);


%magnetic field components produced by disk:

%loops through grid of (x,y) values and creates a matrix of both x and y
%magnetic field components:

n = numel(ticks);
hxmatrix = zeros(n);
for i=1:n
for j=1:n
    hxci = circxfield(a,ticks(j),ticks(i),I);
    hxmatrix(i,j)=hxci;

end
end

hymatrix = zeros(n);
for i=1:n
for j=1:n
    hyci = circyfield(a,ticks(j),ticks(i),I);
    hymatrix(i,j)=hyci;

end
end




%plots  quiver plot of field strength vectors centred at (0,0) with a disk
%superimposed to show the position and relative size of the disk
quiver(ticks,ticks,hxmatrix,hymatrix, 1.2,"color",[0.7,0.6,0.9])
pos = [-a -a 2*a 2*a];
rectangle('Position',pos,'Curvature',[1 1])
xlabel("x-position in $nm$", "Interpreter","latex")
ylabel("y-position in $nm$", "Interpreter","latex")
title("Vector magnetic field surrounding circular current carrying disk")
legend("Relative field strength")
axis equal