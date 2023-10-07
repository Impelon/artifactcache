__all__ = "package_version"

package_name = "artifactcache"
package_version = None

if package_version is None:
    importlib_metadata = None
    try:
        import importlib.metadata as importlib_metadata
    except ImportError:
        try:
            import importlib_metadata
        except ImportError:
            pass
    if importlib_metadata:
        try:
            package_version = importlib_metadata.version(package_name)
        except importlib_metadata.PackageNotFoundError:
            pass

if package_version is None:
    try:
        import pkg_resources
        try:
            package_version = pkg_resources.require(package_name)[0].version
        except pkg_resources.DistributionNotFound:
            pass
    except ImportError:
        pass
