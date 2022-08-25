%Calculates the y Vector component of magnetic field surrounding a circular
%disk of radius a:

function [Hy] = circyfield(a,X,Y,I)
    %a is the radius of the disk
    %X is x position
    %Y is y position
    %I is the value of current through the surface 
    %Returns x component of magnetic field
    p=pi;

    if (X^2+Y^2) >= a^2
        Hy = (I/(2*p))*(1/((X^2+Y^2))) *(-X);

    else 
        Hy = (I/(2*p*(a^2)))*(-X);

    end
end