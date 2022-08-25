%Calculates the x Vector component of magnetic field surrounding a circular
%disk of radius a:

function [Hx] = circxfield(a,X,Y,I)
    %a is the radius of the disk
    %X is x position
    %Y is y position
    %I is the value of current through the surface 
    %Returns x component of magnetic field
    p=pi;

    if (X^2+Y^2) >= a^2
        Hx = (I/(2*p))*(1/((X^2+Y^2))) *(Y);

    else 
        Hx = (I/(2*p*(a^2)))*(Y);

    end
        
end