PURE SUBROUTINE sumImageWithinCircle(ndiv, nx, ny, xmin, xmax, ymin, ymax, r, cx, cy, img, tot)
    ! Import standard modules ...
    USE ISO_C_BINDING

    IMPLICIT NONE

    ! Declare inputs/outputs ...
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: ndiv
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: nx
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: ny
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: r
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cx
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cy
    REAL(kind = C_DOUBLE), DIMENSION(ny, nx), INTENT(in)                        :: img
    REAL(kind = C_DOUBLE), INTENT(out)                                          :: tot

    ! Declare internal variables ...
    INTEGER(kind = C_LONG_LONG)                                                 :: ix
    INTEGER(kind = C_LONG_LONG)                                                 :: iy
    REAL(kind = C_DOUBLE)                                                       :: dx
    REAL(kind = C_DOUBLE)                                                       :: dy
    REAL(kind = C_DOUBLE)                                                       :: frac
    REAL(kind = C_DOUBLE), DIMENSION(nx + 1)                                    :: xaxis
    REAL(kind = C_DOUBLE), DIMENSION(ny + 1)                                    :: yaxis
    REAL(kind = C_DOUBLE), DIMENSION(ny + 1, nx + 1)                            :: dist

    ! Calculate size of pixels ...
    dx = (xmax - xmin) / REAL(ndiv, kind = C_DOUBLE)
    dy = (ymax - ymin) / REAL(ndiv, kind = C_DOUBLE)

    ! Create nodes relative to the centre of the circle ...
    DO ix = 1_C_LONG_LONG, nx + 1_C_LONG_LONG
        xaxis(ix) = xmin + REAL(ix - 1_C_LONG_LONG, kind = C_DOUBLE) * dx - cx
    END DO

    ! Create nodes relative to the centre of the circle ...
    DO iy = 1_C_LONG_LONG, ny + 1_C_LONG_LONG
        yaxis(iy) = ymin + REAL(iy - 1_C_LONG_LONG, kind = C_DOUBLE) * dy - cy
    END DO

    ! Find out the distance of each node to the centre of the circle ...
    DO ix = 1_C_LONG_LONG, nx + 1_C_LONG_LONG
        DO iy = 1_C_LONG_LONG, ny + 1_C_LONG_LONG
            dist(iy, ix) = HYPOT(xaxis(ix), yaxis(iy))
        END DO
    END DO

    ! Initialize total ...
    tot = 0.0e0_C_DOUBLE

    ! Loop over x-axis ...
    DO ix = 1_C_LONG_LONG, nx
        ! Loop over y-axis ...
        DO iy = 1_C_LONG_LONG, ny
            ! Skip this pixel if it is empty ...
            IF(img(iy, ix) == 0.0e0_C_DOUBLE)THEN
                CYCLE
            END IF

            ! Skip this pixel if it is all outside of the circle ...
            IF(ALL(dist(iy:iy + 1_C_LONG_LONG, ix:ix + 1_C_LONG_LONG) >= r))THEN
                CYCLE
            END IF

            ! Check if this pixel is entirely within the circle or if it
            ! straddles the circumference ...
            IF(ALL(dist(iy:iy + 1_C_LONG_LONG, ix:ix + 1_C_LONG_LONG) <= r))THEN
                ! Add all of the value to total ...
                tot = tot + img(iy, ix)
            ELSE
                ! Add part of the value to total ...
                CALL findFractionOfPixelWithinCircle(                           &
                    ndiv = ndiv,                                                &
                    xmin = xaxis(ix),                                           &
                    xmax = xaxis(ix + 1_C_LONG_LONG),                           &
                    ymin = yaxis(iy),                                           &
                    ymax = yaxis(iy + 1_C_LONG_LONG),                           &
                    r = r,                                                      &
                    cx = 0.0e0_C_DOUBLE,                                        &
                    cy = 0.0e0_C_DOUBLE,                                        &
                    frac = frac                                                 &
                )
                tot = tot + img(iy, ix) * frac
            END IF
        END DO
    END DO
END SUBROUTINE sumImageWithinCircle
