PURE SUBROUTINE findFractionOfPixelWithinCircle(ndiv, xmin, xmax, ymin, ymax, r, cx, cy, frac)
    !f2py threadsafe

    ! Import standard modules ...
    USE ISO_C_BINDING

    IMPLICIT NONE

    ! Declare inputs/outputs ...
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: ndiv
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: r
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cx
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cy
    REAL(kind = C_DOUBLE), INTENT(out)                                          :: frac

    ! Declare internal variables ...
    INTEGER(kind = C_LONG_LONG)                                                 :: ix
    INTEGER(kind = C_LONG_LONG)                                                 :: iy
    REAL(kind = C_DOUBLE)                                                       :: dx
    REAL(kind = C_DOUBLE)                                                       :: dy
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:)                            :: xaxis
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:)                            :: yaxis
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:, :)                         :: dist

    ! Allocate arrays ...
    ! NOTE: I decided not to use "sub_allocate_array()" here so as to keep this
    !       subroutine "PURE".
    ALLOCATE(xaxis(ndiv))
    ALLOCATE(yaxis(ndiv))
    ALLOCATE(dist(ndiv, ndiv))

    ! Calculate size of pixels ...
    dx = (xmax - xmin) / REAL(ndiv, kind = C_DOUBLE)
    dy = (ymax - ymin) / REAL(ndiv, kind = C_DOUBLE)

    ! Create centroids relative to the centre of the circle ...
    DO ix = 1_C_LONG_LONG, ndiv
        xaxis(ix) = xmin + (REAL(ix, kind = C_DOUBLE) - 0.5e0_C_DOUBLE) * dx - cx
    END DO

    ! Create centroids relative to the centre of the circle ...
    DO iy = 1_C_LONG_LONG, ndiv
        yaxis(iy) = ymin + (REAL(iy, kind = C_DOUBLE) - 0.5e0_C_DOUBLE) * dy - cy
    END DO

    ! Find out the distance of each centroid to the centre of the circle ...
    DO ix = 1_C_LONG_LONG, ndiv
        DO iy = 1_C_LONG_LONG, ndiv
            dist(iy, ix) = HYPOT(xaxis(ix), yaxis(iy))
        END DO
    END DO

    ! Clean up ...
    DEALLOCATE(xaxis)
    DEALLOCATE(yaxis)

    ! Calculate answer ...
    frac = REAL(COUNT(dist <= r, kind = C_LONG_LONG), kind = C_DOUBLE) / REAL(ndiv * ndiv, kind = C_DOUBLE)

    ! Clean up ...
    DEALLOCATE(dist)
END SUBROUTINE findFractionOfPixelWithinCircle
